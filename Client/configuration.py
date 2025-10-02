configuration = {

    "server": {

        "protocol": "http",
        "host":     "0.0.0.0",
        "port":     5000,
        "apiKey":   "API-Key",

        "request": {

            "delaySeconds": 1,
            "timeoutSeconds": 30

        }

    },

    "search": {

        "idleCores":  1,
        "binaryPath": "../Search Binary/search.out",
        "filePath":   "./results.json"

    },

    "logger": {

        "filePath": "./client.log"

    }

}