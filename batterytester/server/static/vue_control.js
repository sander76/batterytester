var UNKNOWN = {
    v: '-'
}

const STATUS_UNDEFINED = {
    value: 'undefined',
    class: 'status_undefined'
}
const STATUS_FAIL = {
    value: 'failed',
    class: 'status_fail'
}
const STATUS_OK = {
    value: 'ok',
    class: 'status_ok'
}
const STATUS_CONNECTED = {
    value: 'connected',
    class: 'status_connected'
}
const STATUS_DISCONNECTED = {
    value: 'disconnected',
    class: 'status_disconnected'
}

const host = window.location.host
const wsHost = `ws://${host}/ws`
var baseUrl = 'http://' + host

const subjTestFatal = 'test_fatal'
const subjTestFinished = 'test_finished'
const subjTestWarmup = 'test_warmup'
const stateConnected = 'connected'
const stateDisconnected = 'disconnected'

var favIcon = document.getElementById('favicon')

const favError = 'icons/alert-circle.png'
const favRunning = 'icons/rocket.png'
const favFinished = 'icons/thumb-up.png'
const favDisconnected = 'icons/power-plug-off.png'
var currentFavicon = favFinished

function changeFav(state) {
    switch (state) {
        case stateConnected:
            favIcon.href = favFinished
            break
        case stateDisconnected:
            favIcon.href = favDisconnected
            break
        case subjTestFatal:
            favIcon.href = favError
            break
        case subjTestFinished:
            favIcon.href = favFinished
            break
        case subjTestWarmup:
            favIcon.href = favRunning
            break

    }
    //favIcon.href = fav
    //currentFavicon = fav
}

function testData() {
    return {
        started: UNKNOWN,
        test_name: UNKNOWN,
        loop_count: UNKNOWN,
        status: UNKNOWN,
        time_finished: UNKNOWN,
        reason: UNKNOWN
    }
}

function atomData() {
    return {
        identity: UNKNOWN,
        atom_name: UNKNOWN,
        idx: UNKNOWN,
        loop: UNKNOWN,
        status: UNKNOWN,
        started: UNKNOWN,
        duration: UNKNOWN
    }
}

function processData() {
    return {
        _process_name: UNKNOWN,
        _process_id: UNKNOWN,
        _status: UNKNOWN,
        _messages: []
    }
}

function summaryData() {
    return {
        passed: UNKNOWN,
        failed: UNKNOWN,
        failed_ids: UNKNOWN
    }
}

function initialState() {
    return {
        connection: {
            status: STATUS_DISCONNECTED
        },
        test: testData(),
        loop: {},
        atom: atomData(),
        available_tests: [],
        current_test: '',
        sensor_data: [],
        process: processData(),
        summary: summaryData()
    }
}

var data = initialState()

Vue.component('label-value', {
    props: ['label', 'value'],
    template: '<div class="row"><div class="col-sm-6">{{ label }} </div><div class="col-sm-6">{{ value }}</div></div>'
})

Vue.filter('time', function (value) {
    if (value === UNKNOWN.v || value === 'unknown') {
        return UNKNOWN.v
    }
    var date = new Date(value * 1000)
    // return date.toISOString()

    return [date.getHours(), date.getMinutes(), date.getSeconds()].join(':') + ' (' + date.toDateString() + ')'
})
Vue.filter('json', function (value) {
    return JSON.stringify(value, undefined, 4)
})

var vm = new Vue({
    el: '#app',
    data: data,
    methods: {
        get_tests: function (event) {
            this.$http.get('/get_tests').then(response => {
                response.json().then(js => {
                    this.available_tests = js.data
                    this.sync_test()
                })
            }, response => {})
        },
        getStatus: function (event) {
            this.$http.get('/get_status').then(response => {
                response.json().then(js => {
                    for (const key in js) {
                        parseWsMessage(js[key])
                    }
                })
            })
        },
        sync_test: function (event) {
            // Load url query data (test=<testname>) and match it with the available tests
            let queryString = new URLSearchParams(document.location.search.substring(1))
            let test = queryString.get('test')
            this.test_select = test
        },
        clearData: function (event) {
            this.test = testData()
            this.atom = atomData()
            this.summary = summaryData()
            this.process = processData()
            this.sensor_data = []
        },
        startTest: function (event) {
            if (this.current_test === '') {
                window.alert('select a test first')
                return
            }
            this.clearData()
            this.$http.post(baseUrl + '/test_start', {
                test: this.current_test
            }).then(
                response => {}
            )
        },
        stopTest: function (event) {
            this.$http.post(baseUrl + '/test_stop', {
                type: 'stop_test'
            })
        },
        setRoute: function (event) {
            // Set the current test as a url query parameter.
            history.pushState({
                tst: this.current_test
            }, 'no title', '?test=' + this.current_test)
        },
        shutdown: function (event) {
            if (window.confirm('This will cancel the running tests. \n\n Do you want to continue? ')) {
                this.$http.post('/system_shutdown')
            }
        },
        openSocket: function (event) {
            this.ws = new WebSocket(wsHost)
            this.ws.onopen = this.ws_open
            this.ws.onclose = this.ws_close
            this.ws.onmessage = this.ws_message
        },
        ws_open: function (event) {
            console.log('ws opened')
            this.connection.status = STATUS_CONNECTED
            changeFav(stateConnected)
        },
        ws_close: function (event) {
            console.log('ws close')
            this.connection.status = STATUS_DISCONNECTED
            changeFav(stateDisconnected)
        },
        ws_message: function (event) {
            parseWsMessage(JSON.parse(event.data))
        }
    },
    mounted: function () {
        this.get_tests()
        this.openSocket()
        this.getStatus()
    },
    computed: {
        test_select: {
            get: function () {
                return this.current_test
            },
            set: function (newValue) {
                this.current_test = newValue
                this.setRoute()
                console.log('new value set.')
                document.title = this.current_test
            }
        }
    }
})

function merge(source, target) {
    // Merge incomig test data into the existing data.
    for (var key in source) {
        target[key] = source[key]
    }
}

function parseSensor(source, target) {
    for (var item in target) {
        if (target[item]['n'] === source['n']) {
            target[item]['v'] = source['v']
            target[item]['t'] = source['t']
            return
        }
    }
    target.push(source)
}

function parseWsMessage(js) {
    let subj = js['subj']
    let identity = js['identity']
    console.log(subj)


    if (identity === 'test_data') {

        merge(js, vm.test)
        changeFav(subj)
    } else if (identity === 'atom_data') {
        merge(js, vm.atom)
    }
    switch (subj) {
        case 'sensor_data':
            parseSensor(js, vm.sensor_data)
            break

        case 'process_started':
            vm.process = js
            break
        case 'process_info':
            vm.process = js
            break
        case 'result_summary':
            console.log('summary info')
            merge(js, vm.summary)

    }

}
