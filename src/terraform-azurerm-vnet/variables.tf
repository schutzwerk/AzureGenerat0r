variable "vnet_name" {
  description = "Name of the vnet to create"
  default     = "vnet"
}

variable "resource_group_name" {
  description = "Default resource group name that the network will be created in."
}

variable "location" {
  description = "The location/region where the core network will be created. The full list of Azure regions can be found at https://azure.microsoft.com/regions"
  default     = ""
}

variable "address_space" {
  description = "The address space that is used by the virtual network."
  default     = "10.0.0.0/16"
}

# If no values specified, this defaults to Azure DNS 
variable "dns_servers" {
  description = "The DNS servers to be used with vNet."
  default     = []
}

variable "subnet_prefixes" {
  description = "The address prefix to use for the subnet."
  default     = [""]
}

variable "subnet_names" {
  description = "A list of public subnets inside the vNet."
  default     = [""]
}

variable "route_table_ids" {
  description = ""
  default     = [""]
}


variable "own_IP_Address" {
  description = "Own IP Adress for creating NSG. Required for save access to machines with public ip"
  default     = "*"
}