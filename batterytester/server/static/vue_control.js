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
        duration: UNKNOWN,
        reference_data: UNKNOWN
    }
}

function processData() {
    return {
        process_name: '-',
        process_id: '-',
        status: '-',
        messages: [],
        message: '-'
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
            this.current_test = test
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
        },
        set_current_test: function (event) {
            this.current_test = this.process._process_name.v
            this.setRoute()

            document.title = this.current_test
        }
    },
    mounted: function () {
        this.get_tests()
        this.openSocket()
        this.getStatus()
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
    console.log(subj)
    switch (subj) {
        case 'sensor_data':
            parseSensor(js, vm.sensor_data)
            break
        case 'result_summary':
            merge(js, vm.summary)
            break
        case 'process_started':
            merge(js, vm.process)
            vm.set_current_test()
            break
        case 'process_info':
            merge(js, vm.process)
            break
        case 'process_message':
            vm.process.messages.push(js['message'])
            break
        case 'process_finished':
            merge(js, vm.process)
            break
        case 'atom_warmup':
            vm.atom = atomData()
            merge(js, vm.atom)
            break
        case 'atom_execute':
            merge(js, vm.atom)
            break
        case 'atom_collecting':
            merge(js, vm.atom)
            break
        case 'test_warmup':
            merge(js, vm.test)
            changeFav(subj)
            break
        case 'test_finished':
            merge(js, vm.test)
            changeFav(subj)
            break
        case 'test_fatal':
            merge(js, vm.test)
            changeFav(subj)
            break
        case 'test_result':
            merge(js, vm.test)
            changeFav(subj)
            break
    }
    // } else {
    //     switch (identity) {
    //         case 'test_data':
    //             merge(js, vm.test)
    //             changeFav(subj)
    //             break
    //         case 'atom_data':
    //             if (subj === 'atom_warmup') {
    //                 vm.atom = atomData()
    //             }
    //             merge(js, vm.atom)
    //             break
    //         case 'process':
    //             merge(js, vm.process)
    //             switch (subj) {
    //                 case 'process_started':
    //                     //vm.process = js
    //                     vm.set_current_test()
    //                     break
    //                 case 'process_message':
    //                     var msg = js['_message']['v']
    //                     console.log(msg)
    //                     vm.process._messages.push(msg)
    //                     break
    //             }
    //     }
    // }
}
