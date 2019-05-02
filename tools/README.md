# create_thing.py

This tool uses the AWS API (python/boto3)
to create a thing, certificates and attach certificates and policies. In
addition the script outputs ready-to-include C++ code to be included in your
sketch.

## Usage 

```
usage: create_thing.py [-h] [--type-name TYPE_NAME] name policy_name

positional arguments:
  name                  name of the thing to create
  policy_name           policy to attach thing to

optional arguments:
  -h, --help            show this help message and exit
  --type-name TYPE_NAME
                        thing type name
```

## Installation

Run `pipenv install`

## Author and copyright

(C) Copyright 2019 Jan Delgado

## License

MIT
