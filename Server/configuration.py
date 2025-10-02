configuration = {

    "server": {

        "host":   "0.0.0.0",
        "port":   5000,
        "apiKey": "API-Key"

    },

    "search": {

        "filePath": "./search.json",

        "job": {

            "targetDurationSeconds": 600,
            "updateIntervalSeconds": 60,
            "timeoutSeconds":        120

        }

    },

    "logger": {

        "filePath": "./server.log",
        "debug":    True,
        "info":     True,
        "success":  True,
        "warning":  True,
        "error":    True

    }

}