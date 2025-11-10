#!/bin/bash

# Set Java 17 environment for React Native builds
export JAVA_HOME=/home/sakr_quraish/.local/java/jdk-17.0.2
export PATH=$JAVA_HOME/bin:$PATH

# Set Android SDK environment
export ANDROID_HOME=/home/sakr_quraish/Android/Sdk
export ANDROID_SDK_ROOT=$ANDROID_HOME
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/tools:$ANDROID_HOME/tools/bin

echo "Java environment configured:"
echo "JAVA_HOME: $JAVA_HOME"
echo "Java version:"
java -version
echo ""
echo "JDK tools available:"
which javac && echo "✓ javac found"
which jlink && echo "✓ jlink found"
which jar && echo "✓ jar found"
echo ""
echo "Android SDK: $ANDROID_HOME"