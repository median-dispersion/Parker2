configuration = {

    "server": {

        "host":   "0.0.0.0",
        "port":   5000,
        "apiKey": "API-Key"

    },

    "search": {

        "filePath": "./search.json",

        "job": {

            "targetDurationSeconds": 300,
            "updateIntervalSeconds": 30,
            "timeoutSeconds":        60

        }

    },

    "logger": {

        "filePath": "./server.log"

    }

}