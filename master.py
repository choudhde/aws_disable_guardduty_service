####
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
####
__author__ = 'dc'

import boto3
import sys
import argparse
import time


DELEGATED_GUARD_DUTY_ADMIN = '1234567890'


# ##########################################################
# Enable delegated organization admin account
# ###########################################################
def describe_guard_duty(gduty_client):
    try:
        print("List Detectors Function")
        response = gduty_client.list_detectors()['DetectorIds'][0]
        print("Disable Administrator Function")
        disable_delegated_administrator(gduty_client)
        print("Delete Detector")
        response = gduty_client.delete_detector(DetectorId=response)
        print(response)
        print("#"*50)
    except Exception as err:
        print(err)


# ##########################################################
# Enable delegated organization admin account
# ###########################################################
def disable_delegated_administrator(gduty_client):
    try:
        response = gduty_client.disable_organization_admin_account(
                        AdminAccountId=DELEGATED_GUARD_DUTY_ADMIN
                 )
        print(f"{response}")
    except Exception as err:
        print(err)


# #############################
# Delete IAM role for GDuty
# #############################
def delete_gduty_managed_role(client_iam):
    try:
        response = client_iam.delete_service_linked_role(RoleName='AWSServiceRoleForAmazonGuardDuty')
        print(response)
    except Exception as err:
        print(err)


# #############################
# Main Function
# #############################
def main():
    """
    Entry point
    :param event:
    :param context:
    :return:
    """
    parser =argparse.ArgumentParser()
    parser.add_argument('-p', '--profile', help="AWS profile name is required")
    args = parser.parse_args()
    if len(sys.argv) == 2:
        parser.print_help()
        sys.exit(0)
    if args.profile:
        session = boto3.session.Session(
            profile_name=args.profile
        )
    else:
        session = boto3.session.Session(
            profile_name=None
        )
    client = session.client('ec2', region_name='us-east-1')
    regions = [region['RegionName'] for region in client.describe_regions()['Regions']]
    for region in regions:
        try:
            print("#"*50)
            print(f"Region: {region}")
            gduty_client = session.client('guardduty', region_name=region)
            # Enable Guard duty for the control_tower_master/control tower
            describe_guard_duty(gduty_client)
        except Exception as err:
            print(f"{err}")
            continue
    client_iam = session.client('iam')
    time.sleep(5)
    delete_gduty_managed_role(client_iam)


if __name__ == '__main__':
    main()