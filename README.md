# ESP32 AWS IoT example using Arduino SDK

[![Build Status](https://travis-ci.org/jandelgado/esp32-aws-iot.svg?branch=master)](https://travis-ci.org/jandelgado/esp32-aws-iot)


This is a fork of https://github.com/ExploreEmbedded/Hornbill-Examples
focusing on the AWS_IOT library and removing everything else. The code was
also upgraded to AWS IoT Device SDK v3.0.1. 

The library was modified so that the TLS configuration (i.e. certificates and
stuff) is _no longer_ included in the library code self, but is now passed to
the `AWS_IOT` class from the client code. This makes the library easier usable.

* original repository:  https://github.com/ExploreEmbedded/Hornbill-Examples

## Contents


<!-- vim-markdown-toc GFM -->

* [Examples](#examples)
    * [pubSubTest Example](#pubsubtest-example)
* [Build](#build)
* [AWS IoT core notes](#aws-iot-core-notes)
    * [Create thing](#create-thing)
    * [MQTT endpoint](#mqtt-endpoint)
    * [Attach a policy to your thing](#attach-a-policy-to-your-thing)
* [Author](#author)

<!-- vim-markdown-toc -->

## Examples

### pubSubTest Example

Under [examples/pubSubTest](examples/pubSubTest) the original PubSub example of
the hornbill repository is included, with the configuration externalized to a
separate file [config.h-dist](examples/pubSubTest/config.h-dist). To build the
example, copy the `config.h-dist` file to a file called `config.h` and modify
to fit your configuration:

* add WiFi configuration
* add AWS thing private key
* add AWS thing certificate 
* add AWS MQTT endpoint address

## Build

A plattformio [project](platformio.ini) and [Makefile](Makefile) is provided.

* run `make upload monitor` to build and upload the example to the ESP32 and
  start the serial monitor afterwards to see what is going on.

## AWS IoT core notes

**work in progress**

### Create thing

```shell
$ export THING="ESP32_DISPLAY"
$ aws iot list-things    
$ aws iot describe-thing --thing-name "$THING"
$ aws iot create-thing --thing-name "$THING"  \
                       --certificate-pem-outfile=thing_cert.pem
$ aws iot describe-thing --thing-name my_esp32 | jq .thingArn
$ aws iot create-keys-and-certificate --set-as-active \
                                      --certificate-pem-outfile=thing_cert.pem \
                                      --private-key-outfile=thing_key.pem \
$ aws iot describe-thing --thing-name $THING | jq .thingArn
```

### MQTT endpoint

Running `aws describe-endpoint` will give you the endpoint of your MQTT and
REST service:

```shell
$ aws iot describe-endpoint
{
    "endpointAddress": "*****.iot.eu-central-1.amazonaws.com"
}
```

Alternatively, using the AWS console, the MQTT endpoint can be found under
`Test` > `Connected as ...` > `View Endpoint` or `Thing` > `(your thing)` >
`Interact` > `HTTP`. 

The secure MQTT port is 8883. To test if your MQTT endpoint is up, you could
for example issue a netcat command like `nc -v <your-iot-endpoint> 8883`.

### Attach a policy to your thing

It is important to attach a policy to your thing, otherwise no communication
will be possible.

First we need create a permission named `iot-full-permissions` which, as 
the name suggests, has full iot permissions:

```shell
$ cat >thing_policy_full_permissions.json<<EOT
{
   "Version" : "2012-10-17",
   "Statement" : [
      {
         "Action" : [
            "iot:Publish",
            "iot:Connect",
            "iot:Receive",
            "iot:Subscribe",
            "iot:GetThingShadow",
            "iot:DeleteThingShadow",
            "iot:UpdateThingShadow"
         ],
         "Effect" : "Allow",
         "Resource" : [
            "*"
         ]
      }
   ]
}
EOT
$ aws iot create-policy --policy-name "iot-full-permissions" \
                        --policy-document file://thing_policy_full_permissions.json
$ aws iot list-policies
{
    "policies": [
        {
            "policyName": "iot-full-permissions", 
            "policyArn": "arn:aws:iot:eu-central-1:*****:policy/iot-full-permissions"
        }
    ]
}

```
TODO least privilege permission sets 

Next, we attach the policy to our thing (remember, we called it `ESP32_DISPLAY`
when we created it):

```shell
$ aws iot list-things
{
    "things": [
        {
            "thingTypeName": "ESP32",
            "thingArn": "arn:aws:iot:eu-central-1:*****:thing/ESP32_NEOPIXEL_DISPLAY",
            "version": 1,
            "thingName": "ESP32_NEOPIXEL_DISPLAY",
            "attributes": {}
        },
        {
            "thingTypeName": "ESP32",
            "thingArn": "arn:aws:iot:eu-central-1:*****:thing/ESP32_DISPLAY",
            "version": 1,
            "thingName": "ESP32_DISPLAY",
            "attributes": {}
        }
    ]
}
$ aws iot attach-policy --policy-name "iot-full-permissions"  \
                        --target "arn:aws:iot:eu-central-1:*****:thing/ESP32_DISPLAY"
$  aws iot list-targets-for-policy --policy-name iot-full-permissions
```

## Author

Jan Delgado <jdelgado@gmx.net>, original work from https://github.com/ExploreEmbedded/Hornbill-Examples.

