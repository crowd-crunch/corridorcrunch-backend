provider "hcloud" {
  token = "${var.hcloud_token}"
}

resource "hcloud_server" "pz-dev-node-1" {
  name        = "pz-dev-node-1"
  server_type = "cx21"
  image       = "ubuntu-18.04"
  location    = "hel1"
  ssh_keys    = ["${hcloud_ssh_key.pz-dev-node-1-provisioning-key-1.id}"]
}

resource "hcloud_ssh_key" "pz-dev-node-1-provisioning-key-1" {
  name       = "pz-dev-node-1-provisioning-key-1"
  public_key = "${var.hcloud_provisioning_key}"
}


provider "aws" {
  region     = "us-east-1"
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
}

resource "aws_route53_record" "pz-dev-node-1-dns-main" {
  zone_id = "${var.aws_zone_id}"
  name    = "${var.dev_url_fqdn}"
  type    = "A"
  ttl     = "300"
  records = ["${hcloud_server.pz-dev-node-1.ipv4}"]
}

resource "aws_route53_record" "pz-dev-node-1-dns-wildcard" {
  zone_id = "${var.aws_zone_id}"
  name    = "*.${var.dev_url_fqdn}"
  type    = "CNAME"
  ttl     = "300"
  records = ["${var.dev_url_fqdn}"]
}
