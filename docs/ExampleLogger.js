
var ExampleLogger = {}

ExampleLogger.colors = {
      '5': '#ff0066',
      '4': '#e65c00',
      '3': '#809fff',
      '2': '#999999',
      '1': '#737373',
      '0': '#666666',
      'highlight': '#ffff00',
    }

ExampleLogger.log = function (message, severity = 3) {
  if(severity > 5) {
    severity = 5
  } else if (severity < 0) {
    severity = 0
  } else if (!Number.isInteger(severity)) {
    severity = 3
  }

  console.log('<font color="' + this.colors[severity] + '" severity="' + severity + '">' + message + "</font>")
}

ExampleLogger.highlight = function (message) {
  console.log('<font color="' + this.colors['highlight'] + '" type="highlight">' + message + "</font>")
}

module.exports = ExampleLogger
