from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    Tags
)
from constructs import Construct

class SecurityGroupStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 vpc: ec2.IVpc,
                 prefix_lists: dict,
                 config: dict,
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = config.get("env_name", "dr")
        tags = config.get("tags", {})
        security_groups_cfg = config.get("security_groups", {})

        self.security_groups = {}

        for name, rules in security_groups_cfg.items():
            sg = ec2.SecurityGroup(
                self, f"{name}SG",
                vpc=vpc,
                allow_all_outbound=True,
                description=rules.get("description", f"SG for {name}"),
                security_group_name=f"{env_name}-{name}"
            )
            Tags.of(sg).add("Name", f"{env_name}-{name}")
            for k, v in tags.items():
                Tags.of(sg).add(k, v)

            # Ingress rules
            for idx, ingress in enumerate(rules.get("ingress", [])):
                cidr_or_pl = ingress.get("source")
                if cidr_or_pl.startswith("pl-"):
                    cidr_block = ec2.Peer.prefix_list(cidr_or_pl)
                else:
                    cidr_block = ec2.Peer.ipv4(cidr_or_pl)

                sg.add_ingress_rule(
                    peer=cidr_block,
                    connection=ec2.Port(protocol=ingress.get("protocol", "tcp"),
                                        string_representation=ingress.get("description", "rule"),
                                        from_port=ingress.get("from_port"),
                                        to_port=ingress.get("to_port"))
                )

            # Egress rules (optional)
            for idx, egress in enumerate(rules.get("egress", [])):
                cidr_or_pl = egress.get("destination")
                if cidr_or_pl.startswith("pl-"):
                    cidr_block = ec2.Peer.prefix_list(cidr_or_pl)
                else:
                    cidr_block = ec2.Peer.ipv4(cidr_or_pl)

                sg.add_egress_rule(
                    peer=cidr_block,
                    connection=ec2.Port(protocol=egress.get("protocol", "tcp"),
                                        string_representation=egress.get("description", "rule"),
                                        from_port=egress.get("from_port"),
                                        to_port=egress.get("to_port"))
                )

            self.security_groups[name] = sg.security_group_id
