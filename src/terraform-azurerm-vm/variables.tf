variable "resource_group_name" {
  description = "The name of the resource group in which the resources will be created"
  default = ""
}

variable "location" {
  description = "The location/region where the virtual network is created. Changing this forces a new resource to be created."
  default = ""
}


variable "nsg_id" {
  description = "A Network Security Group ID to attach to the network interface"
  default = ""
}

variable "public_ip_dns" {
  description = "Optional globally unique per datacenter region domain name label to apply to each public ip address. e.g. thisvar.varlocation.cloudapp.azure.com where you specify only thisvar here. This is an array of names which will pair up sequentially to the number of public ips defined in var.nb_public_ip. One name or empty string is required for every public ip. If no public ip is desired, then set this to an array with a single empty string."
  default     = [""]
}

variable "admin_password" {
  description = "The admin password to be used on the VMSS that will be deployed. The password must meet the complexity requirements of Azure"
  default     = ""
}

#set on runtime
variable "ssh_key" {
  description = "Path to the public key to be used for ssh access to the VM.  Only used with non-Windows vms and can be left as-is even if using Windows vms. If specifying a path to a certification on a Windows machine to provision a linux vm use the / in the path versus backslash. e.g. c:/home/id_rsa.pub"
  default     = ""
}

variable "remote_port" {
  description = "Remote tcp port to be used for access to the vms created via the nsg applied to the nics."
  default     = ""
}

variable "admin_username" {
  description = "The admin username of the VM that will be deployed"
  default     = ""
}

variable "storage_account_type" {
  description = "Defines the type of storage account to be created. Valid options are Standard_LRS, Standard_ZRS, Standard_GRS, Standard_RAGRS, Premium_LRS."
  default     = ""
}

variable "vm_size" {
  description = "Specifies the size of the virtual machine."
  default     = ""
}

variable "nb_instances" {
  description = "Specify the number of vm instances"
  default     = "1"
}

variable "vm_hostname" {
  description = "local name of the VM"
  default     = "myvm"
}

variable "vm_os_simple" {
  description = "Specify UbuntuServer, WindowsServer, RHEL, openSUSE-Leap, CentOS, Debian, CoreOS and SLES to get the latest image version of the specified os.  Do not provide this value if a custom value is used for vm_os_publisher, vm_os_offer, and vm_os_sku."
  default     = ""
}

variable "vm_os_id" {
  description = "The resource ID of the image that you want to deploy if you are using a custom image.Note, need to provide is_windows_image = true for windows custom images."
  default     = ""
}

variable "is_windows_image" {
  description = "Boolean flag to notify when the custom image is windows based. Only used in conjunction with vm_os_id"
  default     = ""
}

variable "vm_os_publisher" {
  description = "The name of the publisher of the image that you want to deploy. This is ignored when vm_os_id or vm_os_simple are provided."
  default     = ""
}

variable "vm_os_offer" {
  description = "The name of the offer of the image that you want to deploy. This is ignored when vm_os_id or vm_os_simple are provided."
  default     = ""
}

variable "vm_os_sku" {
  description = "The sku of the image that you want to deploy. This is ignored when vm_os_id or vm_os_simple are provided."
  default     = ""
}

variable "vm_os_version" {
  description = "The version of the image that you want to deploy. This is ignored when vm_os_id or vm_os_simple are provided."
  default     = "latest"
}

variable "public_ip_address_allocation" {
  description = "Defines how an IP address is assigned. Options are Static or Dynamic."
  default     = "dynamic"
}

variable "nb_public_ip" {
  description = "Number of public IPs to assign corresponding to one IP per vm. Set to 0 to not assign any public IP addresses."
  default     = "1"
}

variable "delete_os_disk_on_termination" {
  description = "Delete datadisk when machine is terminated"
  default     = ""
}

variable "data_sa_type" {
  description = "Data Disk Storage Account type"
  default     = ""
}

variable "data_disk_size_gb" {
  description = "Storage data disk size size"
  default     = ""
}

variable "data_disk" {
  type        = "string"
  description = "Set to true to add a datadisk."
  default     = "false"
}

variable "number_NICs"{
  default = 1
}

variable "nics_subnet_ids" {
  description = "The subnet id of the virtual network where the virtual machines will reside."
  default = []
}

variable "nics_alloc_type" {
  description = "The subnet id of the virtual network where the virtual machines will reside. Can be 'dynamic' or 'static"
  default = []
}

variable "nics_priv_ip" {
  description = "If alloc type is static, a specified ip-address is used. These are saved in this list. "
  default = []
}