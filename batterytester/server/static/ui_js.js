// connect button
let button = document.getElementById('connect')

button.onclick = connect
// connection status
let connectionStatus = document.getElementById('status')

// shutdown button
let shutdownButton = document.getElementById('shutdown')
shutdownButton.onclick = shutdown

// stop test button
let stopButton = document.getElementById('stop_test_button')
stopButton.onclick = stopTest

// start test button
let startButton = document.getElementById('start_test_button')
startButton.onclick = startTest

// clear data button
let clearButton = document.getElementById('clear_button')
clearButton.onclick = clearData

// all tests button
let allTestButton = document.getElementById('all_tests')
allTestButton.onclick = queryAllTests

// all test list
let allTests = document.getElementById('all_tests_list')

// test info container
let containerTestInfo = document.getElementById('test_info')
let containerAtomInfo = document.getElementById('atom_info')
let containerSummaryInfo = document.getElementById('summary_info')
let containerSensorInfo = document.getElementById('sensor_info')
// area where process output is put in
// let processResultUi = document.getElementById('process_result')

let containerProcessInfo = document.getElementById('process_info')

// var sensorInfo = new StatusElement(document.getElementById('sensor_data'))
// var testInfo = new StatusElement(document.getElementById('test_data'));
// var atomInfo = new StatusElement(document.getElementById('atom_data'));
// var atomSummary = new StatusElement(document.getElementById('summary'))

const host = window.location.host
const wsHost = `ws://${host}/ws`

var baseUrl = 'http://' + host
var ws

let connectStatusDisconnected = 'disconnected'
let connectStatusConnecting = 'connecting'
let connectStatusConnected = 'connected'

let statusTestRunning = 'running'
let statusTestStopped = 'finished'

function openSocket(url) {
    ws = new WebSocket(url) /* globals WebSocket:true */
    ws.onopen = function (event) {
        console.log('connection opened.')
        setConnectionStatus(connectStatusConnected)
        // connectionStatus.innerHTML = 'connected.';
        init()
    }
    ws.onclose = function (event) {
        console.log('websocket connection closed.')
        setConnectionStatus(connectStatusDisconnected)
    }
    ws.onmessage = function (event) {
        var _js = JSON.parse(event.data)
        parseSensor(_js)
    }
}

function httpRequest(method, url, data, callback) {
    // Url must start with an '/'
    var xhr = new XMLHttpRequest()
    xhr.open(method, baseUrl + url, true)
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')

    xhr.send(data)

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var msg = JSON.parse(xhr.responseText)
            callback(msg)
        }
    }
}

function getStatus() {
    function parse(msg) {
        for (const key in msg) {
            if (msg.hasOwnProperty(key)) {
                parseSensor(msg[key])
            }
        }
    }
    httpRequest('GET', '/get_status', null, parse)
}

function setConnectionStatus(statusKey) {
    switch (statusKey) {
        case connectStatusConnected:
            connectionStatus.innerHTML = 'CONNECTED'
            connectionStatus.setAttribute('class', 'bg-success')
            break
        case connectStatusConnecting:
            connectionStatus.innerHTML = 'CONNECTING'
            connectionStatus.setAttribute('class', 'bg-warning')
            break
        case connectStatusDisconnected:
            connectionStatus.innerHTML = 'DISCONNECTED'
            connectionStatus.setAttribute('class', 'bg-error')
            break
    }
}

function clearData() {
    clearValues(containerTestInfo)
    clearValues(containerAtomInfo)
    clearValues(containerSummaryInfo)
    clearSensorData()
    clearValues(containerProcessInfo)
}

function clearSensorData() {
    containerSensorInfo.innerHTML = ''
}

function clearValues(parent) {
    parent.querySelectorAll('.value').forEach(function (node) {
        setUnknown(node)
    })
}

function replaceClass(node, oldValues, newValue) {
    // Adds a new class <newValue> to a current node and deletes
    // a class with name <oldValue>

    var cls = (node.getAttribute('class')).split(' ')
    oldValues.forEach(function (oldValue) {
        var i = 0
        while (i !== -1) {
            i = cls.indexOf(oldValue)
            if (i !== -1) {
                cls.splice(i, 1)
            }
        }
    })

    var i = cls.indexOf(newValue)
    if (i === -1) {
        cls.push(newValue)
    }
    node.setAttribute('class', cls.join(' '))
}

function setKnown(node) {
    // Remove the disable class attribute and change to enabled
    replaceClass(node, ['text-gray'], 'text-primary')
}

function setUnknown(node) {
    replaceClass(node, ['text-primary', 'bg-error', 'bg-success'], 'text-gray')
    node.innerHTML = 'unknown'
}

function init() {
    queryAllTests()
}

function connect(e) {
    if (ws) {
        ws.close()
    }
    clearData()
    setConnectionStatus(connectStatusConnecting)
    openSocket(wsHost)
    getStatus()
}

function shutdown(e) {
    if (window.confirm('This will cancel the running tests. \n\n Do you want to continue? ')) {
        httpRequest('POST', '/system_shutdown', null, null)
    }
}

function stopTest(e) {
    var xhr = new XMLHttpRequest()
    xhr.open('POST', baseUrl + '/test_stop', true)
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')

    xhr.send(JSON.stringify({
        'type': 'stop_test'
    }))

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var msg = JSON.parse(xhr.responseText)
            if (!msg.running) {
                console.log('no test running')
            }
        }
    }
}

function startTest(e) {
    // get selected test.

    var selected = allTests.value
    var xhr = new XMLHttpRequest()
    xhr.open('POST', baseUrl + '/test_start', true)
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    xhr.send(JSON.stringify({
        'test': selected
    }))
}

function queryAllTests(e) {
    function parseAllTests(data) {
        allTests.options.length = 0
        var tests = data['data']
        for (var i = 0; i < tests.length; i++) {
            var option = document.createElement('option')
            option.value = option.text = tests[i]
            allTests.add(option)
        }
    }
    httpRequest('GET', '/get_tests', null, parseAllTests)
    // ws.send(JSON.stringify({
    //     'type': 'all_tests'
    // }))
}

function jsonInterpreter(value) {
    return JSON.stringify(value, undefined, 4)
}

function timeInterpreter(value) {
    if (value === 'unknown') {
        return value
    }

    var date = new Date(value * 1000)
    // return date.toISOString()

    return [date.getHours(), date.getMinutes(), date.getSeconds()].join(':') + ' (' + date.toDateString() + ')'
}

function createListItem(value) {
    var _itm = document.createElement('div')
    _itm.innerHTML = value
    return _itm
}

function parseProcessInfo(data) {
    function parser(key, value, _node) {
        if (value.type === 'status') {
            if (value.v === statusTestRunning) {
                replaceClass(_node, ['bg-error'], 'bg-success')
            } else if (value.v === statusTestStopped) {
                replaceClass(_node, ['bg-success'], 'bg-error')
            }
        } else if (value.type === 'strlist') {
            while (_node.lastChild) {
                _node.removeChild(_node.lastChild)
            }
            value.v.forEach(function (val, index) {
                _node.appendChild(createListItem(val))
            })
        }
        _node.innerHTML = parseValueType(value)
    }
    objectIterator(containerProcessInfo, data, parser)
}

function objectIterator(container, data, parser) {
    // Iterates through a list of nodes which are used to populate
    // test information.
    // We assume per container there is only one class with a specific key.
    // thus using container as a namespace.
    Object.entries(data).forEach(
        function ([key, value], other) {
            var _node = container.querySelector('.' + key)
            if (_node !== null) {
                setKnown(_node)
                console.log(_node)
                parser(key, value, _node)
            }
        }
    )
}

function parseSensorData(data) {
    var _sensorEntry = containerSensorInfo.querySelector('.' + getSensorClassName(data['n']))
    if (_sensorEntry === null) {
        // sensor dom does not exist yet.
        _sensorEntry = createSensorDataContainer(data)
        containerSensorInfo.appendChild(_sensorEntry)
    }
    // sensor data is always a dict.
    var valEntry = _sensorEntry.querySelector('.value')
    valEntry.innerHTML = jsonInterpreter(data['v']['v'])
    var timeEntry = _sensorEntry.querySelector('.time')
    timeEntry.innerHTML = timeInterpreter(data['t']['v'])
}

function parseValueType(value) {
    var _val = value.v
    switch (value.type) {
        case 'time':
            _val = timeInterpreter(_val)
            break
        case 'json':
            _val = jsonInterpreter(_val)
    }
    return _val
}

function parseTestInfo(data) {
    function parser(key, value, _node) {
        if (key === 'status') {
            if (value.v === statusTestRunning) {
                replaceClass(_node, ['bg-error'], 'bg-success')
            } else if (value.v === statusTestStopped) {
                replaceClass(_node, ['bg-success'], 'bg-error')
            }
        }

        _node.innerHTML = parseValueType(value)
    }
    objectIterator(containerTestInfo, data, parser)
}

function parseAtomInfo(data) {
    function parser(key, value, _node) {
        _node.innerHTML = parseValueType(value)
    }
    objectIterator(containerAtomInfo, data, parser)
}

function getSensorClassName(sensorName) {
    return 'sensor_' + sensorName
}

function parseSummaryInfo(data) {
    function parser(key, value, _node) {
        _node.innerHTML = parseValueType(value)
    }
    objectIterator(containerSummaryInfo, data, parser)
}

function createSensorDataContainer(data) {
    function createValueContainer(colwidth, className) {
        var _main = document.createElement('div')
        _main.className = ('column ' + colwidth)
        var _val = document.createElement('div')
        _val.className = className
        _main.appendChild(_val)
        return _main
    }
    var _main = document.createElement('div')

    _main.className = 'columns ' + getSensorClassName(data['n'])
    var _prop = document.createElement('div')
    _prop.className = 'column col-4'
    _prop.innerHTML = data['n']
    _main.appendChild(_prop)

    _main.appendChild(createValueContainer('col-4', 'value'))
    _main.appendChild(createValueContainer('col-4', 'time'))

    return _main
}

function parseSensor(data) {
    let subj = data['subj']
    console.log(subj, data)
    if (subj === 'sensor_data') {
        // Sensor data
        parseSensorData(data)
    } else if (subj === 'atom_warmup') {
        parseAtomInfo(data)
    } else if (subj === 'test_warmup') {
        parseTestInfo(data)
    } else if (subj === 'atom_status') {
        parseAtomInfo(data)
    } else if (subj === 'result_summary') {
        parseSummaryInfo(data)
    } else if (subj === 'test_finished') {
        parseTestInfo(data)
    } else if (subj === 'test_fatal') {
        parseTestInfo(data)
    } else if (subj === 'process_info') {
        parseProcessInfo(data)
    } else if (subj === 'process_started') {
        this.clearData()
        parseProcessInfo(data)
    }
}

connect()
