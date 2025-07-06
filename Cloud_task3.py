# ───────────────────────────────────────────────────────────────
# providers.tf
terraform {
  required_providers {
    multy = {
      source = "multycloud/multy"
      version = ">= 0.3.0"
    }
  }
  required_version = ">= 1.0"
}

variable "clouds" {
  type    = set(string)
  default = ["aws", "azure"]
}

provider "multy" {
  # No extra config needed—authenticated via env vars or CLI
}
# ───────────────────────────────────────────────────────────────
# main.tf
resource "multy_virtual_network" "vn" {
  for_each   = var.clouds
  cloud      = each.key
  name       = "codtech-vnet-${each.key}"
  cidr_block = "10.${each.key == "aws" ? 0 : 1}.0.0/16"
  location   = each.key == "aws" ? "us-east-1" : "eastus"
}

resource "multy_subnet" "subnet" {
  for_each           = var.clouds
  name               = "codtech-subnet-${each.key}"
  cidr_block         = "10.${each.key == "aws" ? 0 : 1}.0.0/24"
  virtual_network_id = multy_virtual_network.vn[each.key].id
}

resource "multy_virtual_machine" "vm" {
  for_each       = var.clouds
  cloud          = each.key
  name           = "codtech-vm-${each.key}"
  size           = "general_micro"
  image_reference = {
    os      = "ubuntu"
    version = "20.04"
  }
  subnet_id = multy_subnet.subnet[each.key].id
  location  = each.key == "aws" ? "us-east-1" : "eastus"
}
# ───────────────────────────────────────────────────────────────
# outputs.tf
output "vm_ips" {
  value = { for c, vm in multy_virtual_machine.vm : c => vm.public_ip }
}
