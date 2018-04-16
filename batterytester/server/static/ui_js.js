// connect button
let button = document.getElementById('connect')

button.onclick = connect
// connection status
let connectionStatus = document.getElementById('status')

// stop test button
let stopButton = document.getElementById('stop_test_button')
stopButton.onclick = stopTest

// start test button
let startButton = document.getElementById('start_test_button')
startButton.onclick = startTest

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
let processResultUi = document.getElementById('process_result')

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
        setConnectionStatus(connectStatusDisconnected)
    }
    ws.onmessage = function (event) {
        var _js = JSON.parse(event.data)
        parseSensor(_js)
    }
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
    clearValues(containerSensorInfo)
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
    replaceClass(node, ['text-primary'], 'text-gray')
}

function init() {
    ws.send(JSON.stringify({
        'type': 'atom'
    })) // Get cached atom data.
    ws.send(JSON.stringify({
        'type': 'test'
    })) // Get cached test data.
    queryAllTests()
}

function connect(e) {
    if (ws) {
        ws.close()
    }
    clearData()
    setConnectionStatus(connectStatusConnecting)
    openSocket(wsHost)
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
    processResultUi.value = ''
    var selected = allTests.value
    var xhr = new XMLHttpRequest()
    xhr.open('POST', baseUrl + '/test_start', true)
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8')
    xhr.send(JSON.stringify({
        'test': selected
    }))

    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var msg = (xhr.responseText)
            processResultUi.value = msg
        }
    }
}

function queryAllTests(e) {
    ws.send(JSON.stringify({
        'type': 'all_tests'
    }))
}

// function StatusElement(parentDiv) {
//     this.dataContainer = {}
//     this.parentDiv = parentDiv
// }

// function plainInterpreter(value) {
//     return value
// }

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

// StatusElement.prototype.clear = function () {
//     this.dataContainer = {}
//     this.parentDiv.innerHTML = ''
// }
// StatusElement.prototype.parse = function (data) {
//     for (const [key, value] of Object.entries(data)) {
//         // Check if there already exists a PropertyElement.
//         var el = this.dataContainer[key]

//         // If PropertyElement does not exist. Create it.
//         if (el === undefined) {
//             var interpreter = plainInterpreter
//             var valueContainer = 'div'
//             if (key === 'reference_data' || key === 'failed_ids') {
//                 interpreter = jsonInterpreter
//                 valueContainer = 'pre'
//             } else if (key === 'started' || key === 'time_finished' || key === 'status_updated' || key ===
//                 't') {
//                 interpreter = timeInterpreter
//             }
//             el = new PropertyElement(key, interpreter, valueContainer)
//             this.dataContainer[key] = el
//             this.parentDiv.appendChild(el.container)
//         }
//         el.update(value)
//     }
// }

// function PropertyElement(key, interpreter, valueContainer) {
//     // A property value container.
//     this.prop = document.createElement('div')
//     this.prop.innerHTML = key
//     this.prop.className = 'sensor_prop'
//     this.val = document.createElement(valueContainer)
//     this.val.className = 'sensor_val'
//     this.container = document.createElement('div')
//     this.container.className = 'sensor_container'
//     this.container.appendChild(this.prop)
//     this.container.appendChild(this.val)
//     this.interpreter = interpreter
// }

// PropertyElement.prototype.update = function (value) {
//     this.val.innerHTML = this.interpreter(value)
//     // if (key === 'reference_data' || key === 'failed_ids') {
//     //     var pre = document.createElement('pre');
//     //     pre.innerHTML = JSON.stringify(value['v'], undefined, 4);
//     //     this.val.appendChild(pre);
//     // } else {
//     //     this.val.innerHTML = value['v'];
//     // }
//     // this.prop.innerHTML = key;
// }

function parseAllTests(data) {
    allTests.options.length = 0
    var tests = data['data']
    for (var i = 0; i < tests.length; i++) {
        var option = document.createElement('option')
        option.value = option.text = tests[i]
        allTests.add(option)
    }
}

function parseProcessResult(data) {
    var _current = processResultUi.value
    _current = _current + '\n' + data.data.log
    processResultUi.value = _current
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
    delete data.subj
    delete data.cache
    console.log(subj, data)
    if (subj === 'sensor_data') {
        // Sensor data
        parseSensorData(data)
    } else if (subj === 'atom_warmup') {
        // Atom data.
        parseAtomInfo(data)
        // atomInfo.parse(data)
    } else if (subj === 'test_warmup') {
        this.clearData()
        // Test data.
        parseTestInfo(data)
    } else if (subj === 'atom_status') {
        parseAtomInfo(data)
        // atomInfo.parse(data)
    } else if (subj === 'result_summary') {
        parseSummaryInfo(data)
    } else if (subj === 'test_finished') {
        parseTestInfo(data)
        // testInfo.parse(data);
    } else if (subj === 'all_tests') {
        parseAllTests(data)
    } else if (subj === 'process_result') {
        parseProcessResult(data)
    } else if (subj === 'test_fatal') {
        parseTestInfo(data)
    }
}

connect()