import json
import readchar
import requests
import sys

OFFLINE_TOKEN = ""
ASSISTED_SERVICE_API = "https://api.openshift.com"
ASSISTED_PORTAL = "https://cloud.redhat.com/openshift/assisted-installer/clusters/"
REDHAT_SSO_REQUEST_TOKEN_URL = "https://sso.redhat.com/auth/realms/redhat-external/protocol/openid-connect/token"
TOKEN = ""
CLUSTER_VERSION = "4.7"
CLUSTER_IMAGE = "quay.io/openshift-release-dev/ocp-release:4.7.13-x86_64"
CLUSTER_CIDR_NET="10.128.0.0/14"
CLUSTER_CIDR_SVC="172.30.0.0/16"
CLUSTER_HOST_PFX=23
PULL_SECRET = ''

def login():
    print("Navigate to https://cloud.redhat.com/openshift/token to get your offline token")
    
    global OFFLINE_TOKEN
    if OFFLINE_TOKEN == "":
        OFFLINE_TOKEN = input("Token: ")

    # Test token
    return request_token(OFFLINE_TOKEN)


def load_pull_secret_from_file():
    print ("Read %sfile" % PULL_SECRET_FILE)
    global PULL_SECRET

    with open(PULL_SECRET_FILE, "r") as reader:
        PULL_SECRET = reader.readlines()[0]
        print("Pull secret succesfully read")

def get_pull_secret():
    if request_token(OFFLINE_TOKEN):
        url = "%s/api/accounts_mgmt/v1/access_token" % ASSISTED_SERVICE_API
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer %s" % TOKEN
        }

        response = requests.post(
            url = url, 
            headers = headers
            )

        if response.status_code == 200:
            print("Retreived pull-secret succesfully")
            return response.json()

        else:
            print("Get pull secret failed.")
            print("Error: " + str(response.status_code))
            print("Message: " + response.text)
            return false


def request_token(offline_token):
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    payload = {
        "grant_type": "refresh_token",
        "client_id": "cloud-services",
        "refresh_token": OFFLINE_TOKEN
    }

    response = requests.post(
        REDHAT_SSO_REQUEST_TOKEN_URL, 
        data = payload, 
        headers = headers
        )
    
    global TOKEN
    
    if response.status_code == 200:
        TOKEN = response.json()["access_token"]
        print("Refresh token succeed")
        return True
    else:
        print("Refresh token failed")
        return False

def list_clusters():
    print("== Assisted Bare Metal CLI - List clusters ==========\n")
    
    if request_token(OFFLINE_TOKEN):
        url = "%s/api/assisted-install/v1/clusters" % ASSISTED_SERVICE_API
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer %s" % TOKEN
        }

        response = requests.get(
            url = url, 
            headers = headers
            )

        if response.status_code == 200:
            r = response.json()
            for cluster in r:
                print(cluster["name"], "user-managed-networking: " + str(cluster["user_managed_networking"]))

        else:
            print("List clusters failed.")
            print("Error: " + str(response.status_code))
            print("Message: " + response.text)
    print("============================================================\n")


def create_cluster():
    print("== Assisted Bare Metal CLI - Create a cluster ==========\n")

    print("This tool will define a new cluster in the Assisted Bare Metal using")
    print("the User Managed Network option. ")
    print("This means the installer will NOT configure VIP, DNS and will NOT do ")
    print("any validation about the networking environment. ")
    print("Make sure you provisionned your own LoadBalancer with DNS entries. \n\n")

    cluster_name = input("Cluster name: ")
    cluster_domain = input("Cluster domain: ")
    cluster_ssh_key = input("SSH allowed public key: ")

    if request_token(OFFLINE_TOKEN):

        data = {
            "kind": "Cluster",
            "name": cluster_name,
            "openshift_version": CLUSTER_VERSION,
            "ocp_release_image": CLUSTER_IMAGE,
            "base_dns_domain": cluster_domain,
            "hyperthreading": "all",
            "cluster_network_cidr": CLUSTER_CIDR_NET,
            "cluster_network_host_prefix": CLUSTER_HOST_PFX,
            "service_network_cidr": CLUSTER_CIDR_SVC,
            "user_managed_networking": True,
            "vip_dhcp_allocation": False,
            "hosts": [],
            "ssh_public_key": cluster_ssh_key,
            "pull_secret": json.dumps(PULL_SECRET)
        }

        url = "%s/api/assisted-install/v1/clusters" % ASSISTED_SERVICE_API
        headers = {
            "Content-type": "application/json",
            "Authorization": "Bearer %s" % TOKEN
        }

        response = requests.post(
            url = url, 
            headers = headers,
            json = data
        )

        if response.status_code == 201:
            r = response.json()
            print("Cluster creation succeed")
            print("You can now continue the installation on the web portal at")
            print(ASSISTED_PORTAL)

        else:
            print("Cluster creation failed.")
            print("Error: " + str(response.status_code))
            print("Message: " + response.text)

    print("============================================================\n")

def main_menu():

    print("== Assisted Bare Metal CLI - User Managed Network ==========")
    
    print(" - [l]  List clusters ")
    print(" - [c]  Create a cluster ")
    print(" - [q]  Quit ")

    print("============================================================")

    choice = readchar.readchar()

    if choice == "l":
        list_clusters()
    elif choice == "c":
        create_cluster()
    elif choice == "p":
        get_pull_secret()
    elif choice == "q":
        quit()

if __name__ == '__main__':
    if login():
        print("Login succeed")
    else:
        print("Login failed")
        sys.exit(1)
    
    PULL_SECRET = get_pull_secret()
    if not PULL_SECRET:
        sys.exit(1)
    
    while True:
        main_menu()