#!/bin/python3.10

import re
import bspc.query
from bspc.classes import Node
from argparse import ArgumentParser, RawTextHelpFormatter
import os


def config() -> ArgumentParser:
    argparser = ArgumentParser(
        description="A scratchpad for bspwm",
        formatter_class=RawTextHelpFormatter
    )

    argparser.add_argument(
        'title_query',
        action='store',
        default='',
        type=str,
        nargs='?',
        help='regex for window titles'
    )

    argparser.add_argument(
        "-c",
        "--class_query",
        "--class",
        default='',
        action='store',
        metavar="class_query",
        type=str,
        help="regex for window classes",
    )

    argparser.add_argument(
        "-r",
        "--run",
        default='',
        type=str,
        help="command when there are no matches",
    )

    argparser.add_argument(
        "-b",
        "--behaviour",
        choices=['i3', 'swap', 'nomark'],
        default='i3',
        help="""<i3> (default)
behaves just like the i3 scratchpad
   
<swap>
hide the current window and show the next in only one command

<nomark>
avoids the use of bspwm marks, with the disadvantage that windows
that are forcibly hidden, their stack positions will be reset""",
    )

    return argparser

args = config().parse_args()

def match_name(node: Node):
    if args.title_query and not re.search(args.title_query, node.name, flags=re.I):
        return False
    elif args.class_query and not re.search(args.class_query, node.className, flags=re.I):
        return False
    return True

hidden_nodes = bspc.query.nodes('.hidden')
floating_nodes = bspc.query.nodes('.floating').sort(lambda x:x.id)

matched = floating_nodes.filter(match_name)

matched_visible = matched - hidden_nodes 
matched_hidden = hidden_nodes & matched 
matched_marked = bspc.query.nodes('.floating.marked') & matched 

matched_focused = (bspc.query.nodes('.focused') & matched_visible).pop() 

if args.behaviour in ['i3', 'swap']:
    if matched_visible:
        next_node = matched_hidden.next(matched_focused)
        for node in matched_visible:
            node.hidden = True
            if next_node:
                node.marked = False

        if next_node:
            next_node.marked = True
            if args.behaviour == 'swap':
                next_node.hidden = False
                next_node.to_monitor('focused', follow=True)
                next_node.focus()
    else:
        matched_marked_hidden = matched_marked & matched_hidden

        if matched_marked_hidden:
            current_node = matched_marked_hidden.first()
        else:
            current_node = matched_hidden.first()

        if current_node:
            current_node.hidden = False
            current_node.to_monitor('focused', follow=True)
            current_node.focus()
        elif args.run:
            os.system(args.run)

elif args.behaviour == 'nomark':
    if matched_visible:
        for node in matched_visible:
            node.hidden = True

        current_node = matched_hidden.next(matched_focused)
    else:
        current_node = matched_hidden.first()

        if args.run and not current_node:
            os.system(args.run)

    if current_node:
        current_node.hidden = False
        current_node.to_monitor('focused', follow=True)
        current_node.focus()

    exit()





