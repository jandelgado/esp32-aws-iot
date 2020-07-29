#!/usr/bin/env python3
"""
use boto to create a thing, attach a policy, attach a certificate and  provide
the private key and certificate as pastable c++ source.

usage: create_thing.py [-h] [--type-name TYPE_NAME] name policy-name

positional arguments:
  name                  name of the thing to create
  policy-name           policy to attach thing to

optional arguments:
  -h, --help            show this help message and exit
  --type-name TYPE_NAME
                        thing type name

(C) Copyright 2019-2020 Jan Delgado
"""
import sys
import argparse
import boto3


def string_as_c_literal(s):
    """return string s as a c multi-line string literal"""
    return "\n".join([ f"\"{l}\\n\"" for l in s.split("\n") ])

def print_key_and_cert(f, cert, thing_name):
    """print key and certificate as c++ source ready to be included in a client sketch """

    print("""
// -------------------------------------------------------------------------
// certificateArn: {arn}
// for thing: {thing_name}
// DO NOT PUT THIS FILE UNDER SOURCE CONTROL.
// -------------------------------------------------------------------------
auto constexpr certificate_pem_crt = {cert};

auto constexpr private_pem_key= {key};

    """.format(arn=cert['certificateArn'],
               thing_name=thing_name,
               cert=string_as_c_literal(cert['certificatePem']),
               key=string_as_c_literal(cert['keyPair']['PrivateKey']),
               file=f))


def create_thing(iot, thing_name, thing_type_name=None):
    kwargs = {'thingName': thing_name}
    if thing_type_name:
        kwargs['thingTypeName'] = thing_type_name
    return iot.create_thing(**kwargs)


def create_keys_and_certificate(iot):
    return iot.create_keys_and_certificate(setAsActive=True)


def attach_thing_principal(iot, thing_name, principal_arn):
    return iot.attach_thing_principal(thingName=thing_name,
                                      principal=principal_arn)


def attach_policy(iot, thing_arn, policy_name):
    return iot.attach_policy(policyName=policy_name, target=thing_arn)


def create_cli_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="name of the thing to create")
    parser.add_argument("policy_name",
                        type=str,
                        help="policy to attach thing to")
    parser.add_argument("--type-name", type=str, help="thing type name")
    return parser


def main(argv):
    parser = create_cli_parser()
    args = parser.parse_args()

    iot = boto3.client('iot')

    thing = create_thing(iot, args.name, args.type_name)
    cert = create_keys_and_certificate(iot)
    attach_thing_principal(iot, args.name, cert['certificateArn'])
    attach_policy(iot, cert['certificateArn'], args.policy_name)

    print("created thing {}".format(thing['thingArn']), file=sys.stderr)
    print("attached certificate {}".format(cert['certificateArn']),
          file=sys.stderr)

    print_key_and_cert(sys.stdout, cert, args.name)


def run():
    main(sys.argv)

if __name__ == '__main__':
    run()

