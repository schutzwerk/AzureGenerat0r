# source: https://github.com/Azure/terraform-azurerm-routetable

resource "azurerm_route_table" "rtable" {
  name                          = "${var.route_table_name}"
  location                      = "${var.location}"
  resource_group_name           = "${var.resource_group_name}"
  disable_bgp_route_propagation = "${var.disable_bgp_route_propagation}"
}

resource "azurerm_route" "route" {
  name                = "${var.route_names[count.index]}"
  resource_group_name = "${var.resource_group_name}"
  route_table_name    = "${azurerm_route_table.rtable.name}"
  address_prefix      = "${var.route_prefixes[count.index]}"
  next_hop_type       = "${var.route_nexthop_types[count.index]}"
  count               = "${length(var.route_names)}"
  next_hop_in_ip_address = "${var.route_next_hop_ip_address[count.index]}"
}
