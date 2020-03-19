# inspired by https://github.com/Azure/terraform-azurerm-vm

module "os" {
  source       = "os"
  vm_os_simple = "${var.vm_os_simple}"
}

resource "azurerm_virtual_machine" "vm-linux" {
  count                         = "${var.vm_os_simple == "WindowsServer" ? 0 : 1}"
  name                          = "${var.vm_hostname}"
  location                      = "${var.location}"
  resource_group_name           = "${var.resource_group_name}"
  vm_size                       = "${var.vm_size}"
  primary_network_interface_id = "${azurerm_network_interface.vm.0.id}"
  network_interface_ids         = ["${azurerm_network_interface.vm.*.id}"]
  delete_os_disk_on_termination = "${var.delete_os_disk_on_termination}"

  storage_image_reference {
    id        = "${var.vm_os_id}"
    publisher = "${var.vm_os_id == "" ? coalesce(var.vm_os_publisher, module.os.calculated_value_os_publisher) : ""}"
    offer     = "${var.vm_os_id == "" ? coalesce(var.vm_os_offer, module.os.calculated_value_os_offer) : ""}"
    sku       = "${var.vm_os_id == "" ? coalesce(var.vm_os_sku, module.os.calculated_value_os_sku) : ""}"
    version   = "${var.vm_os_id == "" ? var.vm_os_version : ""}"
  }

  storage_os_disk {
    name              = "osdisk-${var.vm_hostname}"
    create_option     = "FromImage"
    caching           = "ReadWrite"
    managed_disk_type = "${var.storage_account_type}"
  }

  os_profile {
    computer_name  = "${var.vm_hostname}${count.index}"
    admin_username = "${var.admin_username}"
    admin_password = "${var.admin_password}"
  }

  os_profile_linux_config {
    disable_password_authentication = true

    ssh_keys {
      path     = "/home/${var.admin_username}/.ssh/authorized_keys"
      key_data = "${file("${var.ssh_key}")}"
    }
  }
}



resource "azurerm_virtual_machine" "vm-windows" {
  count                         = "${var.vm_os_simple == "WindowsServer" ? "1": "0"}"
  name                          = "${var.vm_hostname}"
  location                      = "${var.location}"
  resource_group_name           = "${var.resource_group_name}"
  vm_size                       = "${var.vm_size}"
  network_interface_ids         = ["${element(azurerm_network_interface.vm.*.id, count.index)}"]
  delete_os_disk_on_termination = "${var.delete_os_disk_on_termination}"

  storage_image_reference {
    id        = "${var.vm_os_id}"
    publisher = "${var.vm_os_id == "" ? coalesce(var.vm_os_publisher, module.os.calculated_value_os_publisher) : ""}"
    offer     = "${var.vm_os_id == "" ? coalesce(var.vm_os_offer, module.os.calculated_value_os_offer) : ""}"
    sku       = "${var.vm_os_id == "" ? coalesce(var.vm_os_sku, module.os.calculated_value_os_sku) : ""}"
    version   = "${var.vm_os_id == "" ? var.vm_os_version : ""}"
  }

  storage_os_disk {
    name              = "osdisk-${var.vm_hostname}"
    create_option     = "FromImage"
    caching           = "ReadWrite"
    managed_disk_type = "${var.storage_account_type}"
  }

  os_profile {
    computer_name  = "${var.vm_hostname}${count.index}"
    admin_username = "${var.admin_username}"
    admin_password = "${var.admin_password}"
  }

  os_profile_windows_config {
    provision_vm_agent = "true"
    winrm {
      protocol = "HTTP"
    }
  }
}



resource "azurerm_public_ip" "vm" {
  count                        = "${var.nb_public_ip}"
  name                         = "${var.vm_hostname}-publicIP"
  location                     = "${var.location}"
  resource_group_name          = "${var.resource_group_name}"
  public_ip_address_allocation = "${var.public_ip_address_allocation}"
  domain_name_label            = "${element(var.public_ip_dns, count.index)}"
}

resource "azurerm_network_interface" "vm" {
  count                     = "${var.number_NICs}"
  name                      = "nic${count.index}-${var.vm_hostname}"
  location                  = "${var.location}"
  resource_group_name       = "${var.resource_group_name}"

  ip_configuration {
    primary                       = "true"
    name                          = "ipconfig${count.index}"
    subnet_id                     = "${var.nics_subnet_ids[count.index]}"
    private_ip_address_allocation = "${var.nics_alloc_type[count.index]}"
    private_ip_address            = "${var.nics_priv_ip[count.index]}"
    public_ip_address_id          = "${count.index == 0 ? element(concat(azurerm_public_ip.vm.*.id, list("")), 0) : ""}"
  }
}

resource "azurerm_virtual_machine_extension" "vm1ansibleremote" {
    name                      = "vmremotescript1"
    count                     = "${var.vm_os_simple == "WindowsServer" ? "1": "0"}"
    location                  = "${var.location}"
    resource_group_name       = "${var.resource_group_name}"
    virtual_machine_name      = "${azurerm_virtual_machine.vm-windows.name}"
    publisher                 = "Microsoft.Compute"
    type                      = "CustomScriptExtension"
    type_handler_version      = "1.9"
    depends_on                = ["azurerm_virtual_machine.vm-windows"]
    settings = <<SETTINGS
    {
        "fileUris": ["https://raw.githubusercontent.com/ansible/ansible/devel/examples/scripts/ConfigureRemotingForAnsible.ps1"]
    }
    SETTINGS
    protected_settings         = <<PROTECTED_SETTINGS
    {
        "commandToExecute": "powershell.exe -executionpolicy Unrestricted -file ./ConfigureRemotingForAnsible.ps1 -ForceNewSSLCert"
    }
    PROTECTED_SETTINGS
}