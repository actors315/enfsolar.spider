try_index=$(cat .travis.log)

if try_index < 20 then
  export AUTO_TRAVIS_RUN="travis ${try_index}st"
else
  export AUTO_TRAVIS_RUN="skip travis"
fi

try_index=try_index+1

echo try_index > .travis.log