#!/usr/bin/env bash
win=$(bspc query -N -n .hidden.window)
n=$(for w in $win; do
	name=$(xprop -id "$w" WM_CLASS 2>/dev/null | sed -r 's/.+ "(.+)"$/\1/')
	title=$(xprop -id "$w" WM_NAME 2>/dev/null | sed -r 's/.+ "(.+)"$/\1/')
	[ "$name" = "WM_CLASS" ] && echo "node $w" || echo "$name  \"$title\""
done | rofi -dmenu -no-custom -format  i -p 'Unhide: ')
if [ -n "$n" ]; then
	id=$(echo "$win" | sed -n "$((n+1))p")
	bspc node "$id" --flag hidden=off --focus
fi
