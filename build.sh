#!/bin/bash
echo "Verifying python3.5+ version compatibility..."
echo "This may require a package update and temporary sudo access."
if [ $(python3 -c 'import sys; print(sys.version_info[1])') -ge 5 ]; then
  echo "Version is compatible."
else
  echo "Python version requires updating..."
  if [ -n "$(command -v apt-get)" ]; then
    sudo apt-get -qy install python3
  else
    sudo yum install python35
  fi
fi
