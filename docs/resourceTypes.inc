    - multi:
        description: Collection of <<resourcePathName|!pluralize>>.
        get:
            description: |
                Get a list of <<resourcePathName|!pluralize>>.
            responses:
                200:
                    body:
                        application/json:
                404:

    - single:
        description: Object representing <<resourcePathName|!singularize>>.
        get:
            description: |
                Get the <<resourcePathName|!singularize>> with <<resourcePathName|!singularize>>Id = {<<resourcePathName|!singularize>>}.
            responses:
                200:
                    body:
                        application/json:
                404:

