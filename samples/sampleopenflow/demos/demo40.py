#!/usr/bin/python

# Copyright (c) 2015,  BROCADE COMMUNICATIONS SYSTEMS, INC

# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

"""

@authors: Sergei Garbuzov
@status: Development
@version: 1.1.0


"""

import time

from pybvc.controller.controller import Controller
from pybvc.openflowdev.ofswitch import (OFSwitch,
                                        FlowEntry,
                                        Match,
                                        Instruction,
                                        SetNwSrcAction,
                                        SetNwDstAction,
                                        SetTpSrcAction,
                                        SetTpDstAction,
                                        SetFieldAction,
                                        OutputAction)
from pybvc.common.utils import load_dict_from_file
from pybvc.common.status import STATUS
from pybvc.common.constants import (ETH_TYPE_IPv4,
                                    IP_PROTO_TCP,
                                    IP_PROTO_UDP)


def delete_flows(ofswitch, table_id, flow_ids):
    for flow_id in flow_ids:
        result = ofswitch.delete_flow(table_id, flow_id)
        status = result.get_status()
        if(status.eq(STATUS.OK)):
            print ("<<< Flow with id of '%s' successfully removed "
                   "from the Controller" % flow_id)
        else:
            print ("!!!Flow '%s' removal error, reason: %s" %
                   (flow_id, status.brief()))


def of_demo_40():
    f = "cfg.yml"
    d = {}
    if(load_dict_from_file(f, d) is False):
        print("Config file '%s' read error: " % f)
        exit(0)

    try:
        ctrlIpAddr = d['ctrlIpAddr']
        ctrlPortNum = d['ctrlPortNum']
        ctrlUname = d['ctrlUname']
        ctrlPswd = d['ctrlPswd']
        nodeName = d['nodeName']
        rundelay = d['rundelay']
    except:
        print ("Failed to get Controller device attributes")
        exit(0)

    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print ("<<< Demo 40 Start")
    print ("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")

    ctrl = Controller(ctrlIpAddr, ctrlPortNum, ctrlUname, ctrlPswd)
    ofswitch = OFSwitch(ctrl, nodeName)

    print ("<<< 'Controller': %s, 'OpenFlow' switch: '%s'" %
           (ctrlIpAddr, nodeName))

    first_flow_id = 110
    # ---------------------------------------------------
    # First flow entry
    # ---------------------------------------------------
    table_id = 0
    flow_id = first_flow_id
    flow_name = "Modify IP packet example1"
    priority = 900
    cookie = 1300

    match_in_port = 10
    match_eth_type = ETH_TYPE_IPv4
    match_ip_proto = IP_PROTO_TCP
    match_ipv4_src_addr = "192.1.2.0/24"
    match_ipv4_dst_addr = "173.194.123.40/32"
    match_tcp_dst_port = 8080

    act_mod_ipv4_src_addr = "212.16.1.8/32"
    act_mod_ipv4_dst_addr = "52.87.12.11/32"
    act_mod_tcp_src_port = 8888
    act_mod_tcp_dst_port = 9999
    act_out_port = 119

    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Input Port (%s)\n"
           "                Ethernet Type (%s)\n"
           "                IP Protocol (%s)\n"
           "                IPv4 Source Address (%s)\n"
           "                IPv4 Destination Address (%s)\n"
           "                TCP Destination Port (%s)" %
           (match_in_port,
            hex(match_eth_type),
            match_ip_proto,
            match_ipv4_src_addr,
            match_ipv4_dst_addr,
            match_tcp_dst_port))
    print ("        Actions: Modify IPv4 Source Address (%s)\n"
           "                 Modify IPv4 Destination Address (%s)\n"
           "                 Modify TCP Source Port (%s)\n"
           "                 Modify TCP Destination Port (%s)\n"
           "                 Output (%s)" %
           (act_mod_ipv4_src_addr,
            act_mod_ipv4_dst_addr,
            act_mod_tcp_src_port,
            act_mod_tcp_dst_port,
            act_out_port))

    time.sleep(rundelay)

    # Allocate a placeholder for the Flow Entry
    flow_entry1 = FlowEntry()

    # Generic attributes of the Flow Entry
    flow_entry1.set_flow_table_id(table_id)
    flow_entry1.set_flow_name(flow_name)
    flow_entry1.set_flow_id(flow_id)
    flow_entry1.set_flow_cookie(cookie)
    flow_entry1.set_flow_priority(priority)
    flow_entry1.set_flow_hard_timeout(0)
    flow_entry1.set_flow_idle_timeout(0)

    # Instructions/Actions for the Flow Entry
    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = SetNwSrcAction(action_order)
    action.set_nw_src(act_mod_ipv4_src_addr)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetNwDstAction(action_order)
    action.set_nw_dst(act_mod_ipv4_dst_addr)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetTpSrcAction(action_order)
    action.set_tp_src(act_mod_tcp_src_port)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetTpDstAction(action_order)
    action.set_tp_dst(act_mod_tcp_dst_port)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order)
    action.set_outport(act_out_port)
    instruction.add_apply_action(action)

    flow_entry1.add_instruction(instruction)

    # Match Fields for the Flow Entry
    match = Match()

    match.set_in_port(match_in_port)
    match.set_eth_type(match_eth_type)
    match.set_ip_proto(match_ip_proto)
    match.set_ipv4_src(match_ipv4_src_addr)
    match.set_ipv4_dst(match_ipv4_dst_addr)
    match.set_tcp_dst_port(match_tcp_dst_port)

    flow_entry1.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry1.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry1)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))
        exit(0)

    # ---------------------------------------------------
    # Second flow entry
    # ---------------------------------------------------
    table_id = 0
    flow_id += 1
    flow_name = "Modify IP packet example2"
    priority = 900
    cookie = 1300

    match_in_port = 110
    match_eth_type = ETH_TYPE_IPv4
    match_ip_proto = IP_PROTO_UDP
    match_ipv4_src_addr = "10.1.0.0/16"
    match_ipv4_dst_addr = "168.1.1.101/32"
    match_udp_dst_port = 1812

    act_mod_ipv4_src_addr = "172.101.1.9/32"
    act_mod_ipv4_dst_addr = "172.101.1.1/32"
    act_mod_udp_src_port = 5555
    act_mod_udp_dst_port = 7777
    act_out_port = 120

    print "\n"
    print ("<<< Set OpenFlow flow on the Controller")
    print ("        Match:  Input Port (%s)\n"
           "                Ethernet Type (%s)\n"
           "                IP Protocol (%s)\n"
           "                IPv4 Source Address (%s)\n"
           "                IPv4 Destination Address (%s)\n"
           "                UDP Destination Port (%s)" %
           (match_in_port,
            hex(match_eth_type),
            match_ip_proto,
            match_ipv4_src_addr,
            match_ipv4_dst_addr,
            match_udp_dst_port))
    print ("        Actions: Set Field (IPv4 Source Address %s)\n"
           "                 Set Field (IPv4 Destination Address %s)\n"
           "                 Set Field (UDP Source Port %s)\n"
           "                 Set Field (UDP Destination Port %s)\n"
           "                 Output (%s)" %
           (act_mod_ipv4_src_addr,
            act_mod_ipv4_dst_addr,
            act_mod_udp_src_port,
            act_mod_udp_dst_port,
            act_out_port))

    time.sleep(rundelay)

    # Allocate a placeholder for the Flow Entry
    flow_entry2 = FlowEntry()

    # Generic attributes of the Flow Entry
    flow_entry2.set_flow_table_id(table_id)
    flow_entry2.set_flow_name(flow_name)
    flow_entry2.set_flow_id(flow_id)
    flow_entry2.set_flow_cookie(cookie)
    flow_entry2.set_flow_priority(priority)
    flow_entry2.set_flow_hard_timeout(0)
    flow_entry2.set_flow_idle_timeout(0)

    # Instructions/Actions for the Flow Entry
    instruction = Instruction(instruction_order=0)

    action_order = 0
    action = SetFieldAction(action_order)
    action.set_ipv4_src(act_mod_ipv4_src_addr)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_ipv4_dst(act_mod_ipv4_dst_addr)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_udp_src_port(act_mod_udp_src_port)
    instruction.add_apply_action(action)

    action_order += 1
    action = SetFieldAction(action_order)
    action.set_udp_dst_port(act_mod_udp_dst_port)
    instruction.add_apply_action(action)

    action_order += 1
    action = OutputAction(action_order)
    action.set_outport(act_out_port)
    instruction.add_apply_action(action)

    flow_entry2.add_instruction(instruction)

    # Match Fields for the Flow Entry
    match = Match()

    match.set_in_port(match_in_port)
    match.set_eth_type(match_eth_type)
    match.set_ip_proto(match_ip_proto)
    match.set_ipv4_src(match_ipv4_src_addr)
    match.set_ipv4_dst(match_ipv4_dst_addr)
    match.set_udp_dst_port(match_udp_dst_port)

    flow_entry2.add_match(match)

    print ("\n")
    print ("<<< Flow to send:")
    print flow_entry2.get_payload()
    time.sleep(rundelay)
    result = ofswitch.add_modify_flow(flow_entry2)
    status = result.get_status()
    if(status.eq(STATUS.OK)):
        print ("<<< Flow successfully added to the Controller")
    else:
        print ("\n")
        print ("!!!Demo terminated, reason: %s" % status.detailed())
        delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))
        exit(0)

    print ("\n")
    print ("<<< Delete flows from the Controller's cache "
           "and from the table '%s' on the '%s' node" % (table_id, nodeName))
    time.sleep(rundelay)
    delete_flows(ofswitch, table_id, range(first_flow_id, flow_id+1))

    print ("\n")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print (">>> Demo End")
    print (">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

if __name__ == "__main__":
    of_demo_40()
