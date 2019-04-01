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

function changeFav(state) {
    switch (state) {
        case stateConnected:
            console.log('Icon to: ' + favFinished)
            favIcon.href = favFinished
            break
        case stateDisconnected:
            console.log('Icon to: ' + favDisconnected)
            favIcon.href = favDisconnected
            break
        case subjTestFatal:
            console.log('Icon to: ' + favError)
            favIcon.href = favError
            break
        case subjTestFinished:
            console.log('Icon to: ' + favFinished)
            favIcon.href = favFinished
            break
        case subjTestWarmup:
            console.log('Icon to: ' + favRunning)
            favIcon.href = favRunning
            break
    }
}

function loopData() {
    return {
        duration: UNKNOWN,
        atoms: []
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

// function summaryData() {
//     return {
//         passed: UNKNOWN,
//         failed: UNKNOWN,
//         failed_ids: undefined
//     }
// }

function summaryData() {
    return {
        passed: UNKNOWN,
        failed: UNKNOWN,
        failed_ids: {
            "v": [{
                "idx": undefined,
                "loop": undefined,
                "reason": undefined,
                "atom_name": undefined,
                "data": {}
            }]
        }
    }
}

function currentTest() {
    return {}
}

function initialState() {
    return {
        connection: {
            status: STATUS_DISCONNECTED
        },
        test: testData(),
        loop: loopData(),
        atom: atomData(),
        available_tests: [],
        current_test: currentTest(),
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

Vue.component('key-val', {
    props: ['label'],
    template: '<div class="row"><div class="col-sm-6">{{ label }} </div><div class="col-sm-6"><slot></slot></div></div>'
})

Vue.component('atom-item', {
    props: ['atom', 'index', 'activeidx'],
    data: function () {
        return {
            current: true
        }
    },
    computed: {
        selected: function () {
            return {
                current_atom: this.index === this.activeidx
            }
        },
        mounted() {
            this.timer = setInterval(this.updateDateTime, 1000)
        }
    },
    template: '<div v-bind:class="selected" class="atoms"><div class="circular">{{index}}</div> {{ atom.atom_name.v}} </div>'
})

Vue.component('timer', {
    props: ['start', 'started'],
    data: function () {
        return {
            time: 0,
            timer: undefined
        }
    },
    // mounted() {
    //     this.timer = setInterval(this.updateTimer, 1000)
    // },
    beforeDestroy() {
        clearInterval(this.timer)
    },
    watch: {
        start: function (val) {
            var now = Date.now() / 1000
            var diff = now - this.started
            console.debug("seconds already passed: ", diff)

            this.time = val - Math.floor(diff)
            this.startTimer()
        }
    },
    methods: {
        startTimer() {
            if (this.timer === undefined) {
                this.timer = setInterval(this.updateTimer, 1000)
                console.log("starting timer: ", this.timer)
            }
        },
        stopTimer() {
            clearInterval(this.timer)
            console.log("stopping timer ", this.timer)
            this.timer = undefined
        },
        updateTimer() {
            //console.log("updating timer")
            if (this.time <= 0) {
                this.stopTimer()
            } else {
                this.time -= 1
            }
        }
    },
    template: '<span> {{ time }} </span>'
})

Vue.filter('time', function (value) {
    if (value === UNKNOWN.v || value === 'unknown') {
        return UNKNOWN.v
    }
    var date = new Date(value * 1000)
    // return date.toISOString()

    return [date.getHours(), date.getMinutes(), date.getSeconds()].join(':') + ' (' + date.toDateString() + ')'
    //return moment.unix(value).format('MMMM Do YYYY, HH:mm:ss')
})
Vue.filter('duration', function (value) {
    if (value === UNKNOWN.v || value === 'unknown') {
        return UNKNOWN.v
    }
    var hr = Math.floor(value / 3600)
    var rem = value % 3600
    var min = Math.floor(rem / 60)
    var sec = rem % 60
    if (hr) {
        return hr + "hr " + min + "min " + sec + "sec"
    }
    if (min) {
        return min + "min " + sec + "sec"
    }
    return sec + "sec"
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
        find_test_by_name: function (name) {
            console.log('finding test name: ' + name)
            for (var i = 0; i < this.available_tests.length; i++) {
                if (this.available_tests[i].name === name) {
                    return this.available_tests[i]
                }
            }
            return {}
        },
        sync_test: function (event) {
            // Load url query data (test=<testname>) and match it with the available tests
            let queryString = new URLSearchParams(document.location.search.substring(1))
            let test = queryString.get('test')
            if (test != null) {
                this.current_test = this.find_test_by_name(test)
            }
        },
        clearData: function (event) {
            this.test = testData()
            this.atom = atomData()
            this.summary = summaryData()
            this.process = processData()
            this.sensor_data = []
        },
        startTest: function (event) {
            if (this.current_test === {}) {
                window.alert('select a test first')
                return
            }
            this.clearData()
            this.$http.post(baseUrl + '/test_start', this.current_test).then(
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
            }, 'no title', '?test=' + this.current_test.name)
        },
        shutdown: function (event) {
            if (window.confirm('This will cancel the running tests. \n\n Do you want to continue? ')) {
                this.$http.post('/system_shutdown')
            }
        },
        update: function (event){
            if (window.confirm("This will cancel the running test. \n\n Do you want to continue? ")){
                this.$http.post("/system_update").then(response => {
                response.json().then(js => {

                })
            }, response => {})
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
            this.get_tests()
            this.getStatus()
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
            console.log("test process name: " + this.process.process_name)
            this.current_test = this.find_test_by_name(this.process.process_name)
            this.setRoute()

            document.title = this.current_test.name
        }
    },
    mounted: function () {
        this.openSocket()
    }

})

function merge(source, target) {
    // Merge incomig test data into the existing data.
    try{
        for (var key in source) {
            target[key] = source[key]
        }}
    catch(error){
        console.error(error)
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
//            merge(js, vm.summary)
            break
        case 'process_started':
            merge(js, vm.process)
            vm.set_current_test()
            break
        case 'process_info':
            merge(js, vm.process)
            vm.set_current_test()
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
        case 'loop_warmup':
            merge(js, vm.loop)
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
        case 'sensor_cache':
            for (var sensor in js) {
                if (sensor !== 'subj') {
                    parseSensor(js[sensor], vm.sensor_data)
                }
            }
            break
    }
}
