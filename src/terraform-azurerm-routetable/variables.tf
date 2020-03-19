variable "resource_group_name" {
  description = "Default resource group name that the network will be created in."
  default = ""
}

variable "location" {
  description = "The location/region where the core network will be created. The full list of Azure regions can be found at https://azure.microsoft.com/regions"
  default     = ""
}

variable "route_table_name" {
  description = "The name of the RouteTable being created."
  default     = "routetable"
}

variable "disable_bgp_route_propagation" {
  description = "Boolean flag which controls propagation of routes learned by BGP on that route table. True means disable."
  default     = "true"
}

variable "route_prefixes" {
  description = "The list of address prefixes to use for each route."
  default     = []
}

variable "route_names" {
  description = "A list of public subnets inside the vNet."
  default     = []
}

variable route_nexthop_types {
  description = "The type of Azure hop the packet should be sent to for each corresponding route.Valid values are 'VirtualNetworkGateway', 'VnetLocal', 'Internet', 'HyperNetGateway', 'None'"
  default     = []
}

variable "route_next_hop_ip_address" {
  description = ""
  default = []
}