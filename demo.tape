# Records docs/demo.gif automatically.
#   brew install charmbracelet/tap/vhs
#   vhs demo.tape
#
# Requires the oops shell hook to be active. If `oops` doesn't trigger inside
# the recording, swap the `Type "oops"` lines for: Type `oops-fix "$(fc -ln -1)"`

Output docs/demo.gif

Set FontSize 22
Set Width 1100
Set Height 600
Set Theme "Dracula"
Set Padding 20
Set TypingSpeed 80ms

# let the prompt settle
Sleep 800ms

# a classic typo everyone recognizes
Type "git statsu"
Sleep 400ms
Enter
Sleep 1s

# the magic word
Type "oops"
Sleep 400ms
Enter

# wait for: reproduce -> thinking -> suggestion + prompt
Sleep 3500ms

# accept the fix
Type "y"
Enter
Sleep 2s
