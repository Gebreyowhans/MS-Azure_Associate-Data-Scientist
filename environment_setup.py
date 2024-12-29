
from azureml.core import Workspace
from azureml.core.authentication import InteractiveLoginAuthentication
from azureml.core.compute import ComputeInstance, AmlCompute, ComputeTarget
from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient

import os
import json
import random
import subprocess
import os

# Define Azure ML details


def get_subscription_id():

    # Fetch subscription ID securely from environment variables or dynamically

    # Option 1: Store subscription ID as an environment variable
    subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")

    # Option 2: Fetch subscription ID dynamically
    if not subscription_id:
        subscription_id = subprocess.check_output(
            ["az", "account", "show", "--query", "id", "-o", "tsv"], text=True
        ).strip()

    if not subscription_id:
        raise ValueError(
            "Could not retrieve subscription ID. Set it as an environment variable.")

    return subscription_id
# Function to execute Azure CLI commands


def execute_command(command):
    try:
        result = subprocess.check_output(command, shell=True, text=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}")
        return None

# Provision Azure Compute Resources


def provision_compute(resource_group, workspace_name):
    # Provision the compute instance
    compute_instance_name = "cigebre"
    compute_instance_size = "STANDARD_DS11_V2"
    print(f"Provisioning Compute Instance: {compute_instance_name}")
    execute_command(
        f"az ml compute create --name {compute_instance_name} "
        f"--size {compute_instance_size} --type ComputeInstance --resource-group {resource_group} "
        f"--workspace-name {workspace_name}"
    )

    # Provision the compute cluster
    compute_cluster_name = "aml-cluster"
    compute_cluster_size = "STANDARD_DS11_V2"
    max_instances = 2
    print(f"Provisioning Compute Cluster: {compute_cluster_name}")
    execute_command(
        f"az ml compute create --name {compute_cluster_name} "
        f"--size {compute_cluster_size} --max-instances {max_instances} --type AmlCompute "
        f"--resource-group {resource_group} --workspace-name {workspace_name}"
    )

# Connect to Azure Machine Learning Workspace


def provision_resource(subscription_id, resource_group, workspace_name, region):
    print("Connecting to Azure Machine Learning Workspace...")
    try:

        # Authenticate and create a workspace object
        interactive_auth = InteractiveLoginAuthentication()

        # Create the workspace
        ws = Workspace.create(name=workspace_name,
                              subscription_id=subscription_id,
                              resource_group=resource_group,
                              location=region,
                              auth=interactive_auth)
        return ws
    except Exception as e:
        print(f"Failed to provision resource : {e}")
        return None

# Connect to Azure Machine Learning Workspace


def connect_to_workspace(subscription_id, resource_group, workspace_name):
    print("Connecting to Azure Machine Learning Workspace...")
    try:
        workspace = Workspace(subscription_id=subscription_id,
                              resource_group=resource_group, workspace_name=workspace_name)
        print(f"Connected to workspace: {workspace.name}")
        return workspace
    except Exception as e:
        print(f"Failed to connect to workspace: {e}")
        return None


def delete_resources(subscription_id):

    # Define the subscription ID and initialize the credential and client
    credential = DefaultAzureCredential()

    # Initialize the ResourceManagementClient
    resource_client = ResourceManagementClient(credential, subscription_id)

    # List all resource groups
    resource_groups = resource_client.resource_groups.list()

    # Iterate through each resource group and delete resources within it
    for rg in resource_groups:
        print(f"Deleting resources in Resource Group: {rg.name}")

        # List resources within the resource group
        resources = resource_client.resources.list_by_resource_group(rg.name)

        # Delete each resource
        for resource in resources:
            print(
                f"Deleting resource: {resource.name} of type {resource.type}")
            resource_client.resources.begin_delete_by_id(
                resource.id, api_version='2021-04-01')


    # Main script
if __name__ == "__main__":
    subscription_id = get_subscription_id()
    resource_group = "rg-dp100-gebre"
    workspace_name = "mlw-dp100-gebre"

    config_path = "config.json"

    # Choose a random region from the available options
    selected_region = random.choice(
        ["eastus", "westus", "centralus", "canadaeast"])
    print(f"Selected region: {selected_region}")

    # provision_resource
    ws = provision_resource(subscription_id=subscription_id, resource_group=resource_group,
                            workspace_name=workspace_name, region=selected_region)

    # Connect to workspace
    # ws = connect_to_workspace(subscription_id, resource_group,ws.name)

    # Provision resources
    # provision_compute(resource_group, workspace_name)
