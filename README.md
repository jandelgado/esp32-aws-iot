# ESP32 AWS IoT example using Arduino SDK

[![Build Status](https://travis-ci.org/jandelgado/esp32-aws-iot.svg?branch=master)](https://travis-ci.org/jandelgado/esp32-aws-iot)

This is a fork of https://github.com/ExploreEmbedded/Hornbill-Examples
focusing on the AWS_IOT library and removing everything else. The code was
also upgraded to AWS IoT Device SDK v3.0.1.

The library was modified so that the TLS configuration (i.e. certificates and
stuff) is _no longer_ included in the library code self, but is now passed to
the `AWS_IOT` class from the client code. This makes the library easier usable.

* original repository:  https://github.com/ExploreEmbedded/Hornbill-Examples

Additionally, I added a tutorial on using the AWS cli to create everything
needed to set your ~~thing~~ up.

## Contents

<!-- vim-markdown-toc GFM -->

* [Examples](#examples)
    * [pubSubTest Example](#pubsubtest-example)
* [Build](#build)
* [AWS IoT core notes](#aws-iot-core-notes)
    * [Create thing group and thing](#create-thing-group-and-thing)
    * [Create keys and certificates](#create-keys-and-certificates)
    * [Attach policy to your thing](#attach-policy-to-your-thing)
    * [MQTT endpoint](#mqtt-endpoint)
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
* add AWS thing private key (see below)
* add AWS thing certificate (see below)
* add [AWS MQTT endpoint address](#mqtt-endpoint)

## Build

A plattformio [project](platformio.ini) and [Makefile](Makefile) is provided.

* run `make upload monitor` to build and upload the example to the ESP32 and
  start the serial monitor afterwards to see what is going on.

## AWS IoT core notes

**Work in progress**

This chapter describes how to use the AWS cli to

* create a thing type and thing
* create keys and certificates for a thing
* attach a certificate to a thing
* create and attach a policy to a thing

### Create thing group and thing

We use the AWS cli to create a thing type called `ESP32` and a thing with the
name `ESP32_SENSOR`. For convenience and later reference, we store the things
name in the environment variable `THING`.

```bash
$ export THING="ESP32_SENSOR"
$ aws iot create-thing-type --thing-type-name "ESP32"
$ aws iot list-thing-types
{
    "thingTypes": [
        {
            "thingTypeName": "ESP32",
            "thingTypeProperties": {
                "thingTypeDescription": "ESP32 devices"
            },
            "thingTypeMetadata": {
                "deprecated": false,
                "creationDate": 1530358342.86
            },
            "thingTypeArn": "arn:aws:iot:eu-central-1:*****:thingtype/ESP32"
        }
    ]
}
$ aws iot create-thing --thing-name "$THING" --thing-type-name "ESP32"
$ aws iot list-things
{
    "things": [
        {
            "thingTypeName": "ESP32",
            "thingArn": "arn:aws:iot:eu-central-1:*****:thing/ESP32_SENSOR",
            "version": 1,
            "thingName": "ESP32_SENSOR",
            "attributes": {}
        }
    ]
}
```

### Create keys and certificates

```bash
$ aws iot create-keys-and-certificate --set-as-active \
                                      --certificate-pem-outfile="${THING}_cert.pem" \
                                      --private-key-outfile="${THING}_key.pem"
{
    "certificateArn": "arn:aws:iot:eu-central-1:*****:cert/7bb8fd75139186deef4c054a73d15ea9e2a5f603a29025e453057bbe70c767fe",
    "certificatePem": "-----BEGIN CERTIFICATE-----\n ... \n-----END CERTIFICATE-----\n",
    "keyPair": {
        "PublicKey": "-----BEGIN PUBLIC KEY-----\n ... \n-----END PUBLIC KEY-----\n",
        "PrivateKey": "-----BEGIN RSA PRIVATE KEY-----\n ... \n-----END RSA PRIVATE KEY-----\n"
    },
    "certificateId": "7bb8fd75139186deef4c054a73d15ea9e2a5f603a29025e453057bbe70c767fe"
}

```

On the thing we later need (see [config.h-dir](examples/pubSubTest/config.h-dist)):

* the private key stored in `${THING}_key.pem` (i.e. `ESP32_SENSOR_key.pem`)
* the certificate stored in `${THING}_cert.pem` (i.e. `ESP32_SENSOR_cert.pem`)

Note that this is the only time that the private key will be output by AWS.

Next we attach the certificate to the thing:

```bash
$ aws iot attach-thing-principal --thing-name "$THING" \
         --principal "arn:aws:iot:eu-central-1:*****:cert/7bb8fd75139186deef4c054a73d15ea9e2a5f603a29025e453057bbe70c767fe"
$ aws iot list-principal-things --principal  "arn:aws:iot:eu-central-1:*****:cert/7bb8fd75139186deef4c054a73d15ea9e2a5f603a29025e453057bbe70c767fe"
{
    "things": [
        "ESP32_SENSOR"
    ]
}
aws iot list-thing-principals --thing-name $THING
{
    "principals": [
        "arn:aws:iot:eu-central-1:*****:cert/7bb8fd75139186deef4c054a73d15ea9e2a5f603a29025e453057bbe70c767fe"
    ]
}
```

### Attach policy to your thing

It is important to attach a policy to your thing, otherwise no communication
will be possible.

First we need create a permission named `iot-full-permissions` which, as
the name suggests, has full iot permissions:

```bash
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

(TODO least privilege permission sets in policies)

Next, we attach the policy to our thing (remember, we called it `ESP32_SENSOR`
and stored the name in the `$THING` environment variable when we created it):

```bash
$ THING_ARN=$(aws iot describe-thing --thing-name $THING | jq .thingArn)
$ echo $THING_ARN
"arn:aws:iot:eu-central-1:*****:thing/ESP32_SENSOR"
$ aws iot attach-policy --policy-name "iot-full-permissions"  \
                        --target "$THING_ARN"
$ aws iot list-targets-for-policy --policy-name iot-full-permissions
...
```

### MQTT endpoint

Running `aws describe-endpoint` will give you the endpoint of your MQTT and
REST service:

```bash
$ aws iot describe-endpoint
{
    "endpointAddress": "*****.iot.eu-central-1.amazonaws.com"
}
```

The secure MQTT port is 8883. To test if your MQTT endpoint is up, you could
for example issue a netcat command like `nc -v <your-iot-endpoint> 8883`.

## Author

Jan Delgado <jdelgado@gmx.net>, original work from https://github.com/ExploreEmbedded/Hornbill-Examples.

