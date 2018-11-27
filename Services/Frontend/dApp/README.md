## Adding a Front-end for your Service on dApp

### 1. This tutorial is for the [alpha](http://alpha.singularitnet.io/) version of the SingularityNET dApp

### 2. Cloning the [alpha-app](https://github.com/singnet/alpha-dapp)
```
$ mkdir /opt/snet
$ cd /opt/snet
$ git clone https://github.com/singnet/alpha-dapp
$ cd alpha-dapp
```

### 3. Checking all the Services with frontend
```
$ cd src/components/service
$ ls -la
total 72
drwxrwxr-x 2 user user 4096 Ago 23 09:07 .
drwxrwxr-x 3 user user 4096 Ago 23 09:06 ..
-rw-rw-r-- 1 user user 4166 Ago 23 09:06 alpha_example.js
-rw-rw-r-- 1 user user 3073 Ago 23 09:06 default.js
-rw-rw-r-- 1 user user 2580 Ago 23 09:06 exchange.js
-rw-rw-r-- 1 user user 4694 Ago 23 09:06 face_alignment.js
-rw-rw-r-- 1 user user  468 Ago 23 09:06 face_detect.css.js
-rw-rw-r-- 1 user user 4683 Ago 23 09:06 face_detect.js
-rw-rw-r-- 1 user user  468 Ago 23 09:06 face_landmarks.css.js
-rw-rw-r-- 1 user user 6562 Ago 23 09:06 face_landmarks.js
-rw-rw-r-- 1 user user 4543 Ago 23 09:06 face_recognition.js
```
This is the folder where your frontend file has to be.
You can use some of these available services to help you understand how to build your own.

### 4. Adding your Service's frontend file

Once your service .js file is ready, just copy and paste it inside `service/`
```
$ mv ~/cnn_image_recon.js .
$ ls -la
total 72
drwxrwxr-x 2 user user 4096 Ago 23 09:07 .
drwxrwxr-x 3 user user 4096 Ago 23 09:06 ..
-rw-rw-r-- 1 user user 4166 Ago 23 09:06 alpha_example.js
-rw-rw-r-- 1 user user 3073 Ago 23 09:06 default.js
-rw-rw-r-- 1 user user 2580 Ago 23 09:06 exchange.js
-rw-rw-r-- 1 user user 4694 Ago 23 09:06 face_alignment.js
-rw-rw-r-- 1 user user  468 Ago 23 09:06 face_detect.css.js
-rw-rw-r-- 1 user user 4683 Ago 23 09:06 face_detect.js
-rw-rw-r-- 1 user user  468 Ago 23 09:06 face_landmarks.css.js
-rw-rw-r-- 1 user user 6562 Ago 23 09:06 face_landmarks.js
-rw-rw-r-- 1 user user 4543 Ago 23 09:06 face_recognition.js
-rw-rw-r-- 1 user user 7359 Ago 23 17:41 cnn_image_recon.js
```

### 5. Making your frontend file visible for dApp

Now you have to add your service to the dApp `index.js`
```
$ cd /opt/snet/alpha-dapp/src
$ ls -la
total 32
drwxrwxr-x 3 user user 4096 Ago 23 17:54 .
drwxrwxr-x 9 user user 4096 Ago 23 18:07 ..
drwxrwxr-x 3 user user 4096 Ago 23 09:06 components
-rw-rw-r-- 1 user user 1436 Ago 23 09:06 index.html
-rw-rw-r-- 1 user user 7460 Ago 23 17:54 index.js
-rw-rw-r-- 1 user user 2862 Ago 23 09:06 jsonrpc.js
-rw-rw-r-- 1 user user 3076 Ago 23 09:06 util.js
$ nano index.js
```
Make 2 additions to `index.js`

```
import DefaultService from './components/service/default';
import AlphaExampleService from './components/service/alpha_example';
import FaceDetectService from './components/service/face_detect';
import FaceLandmarksService from './components/service/face_landmarks';
import FaceAlignmentService from './components/service/face_alignment';
import FaceRecognitionService from './components/service/face_recognition';
import ExchangeService from './components/service/exchange';
// Fist addition
import CNN_ImageRecon from './components/service/cnn_image_recon';

...

    this.serviceNameToComponent = {
      'Alpha TensorFlow Agent': AlphaExampleService,
      'face_detect': FaceDetectService,
      'face_landmarks': FaceLandmarksService,
      'face_alignment': FaceAlignmentService,
      'face_recognition': FaceRecognitionService,
      'Exchange AGI for BTC': ExchangeService,
      // Second Addition
      'SNET_BH/CNN_ImageRecon': CNN_ImageRecon
    };
```
In this example the service was created with the name "CNN_ImageRecon" under the organization "SNET_BH".

### 6. Testing:

To test your frontend file you must run the dApp in an online host (like AWS-EC2).
(Make sure that the port is opened for external access on your host.)

Edit the `package.json` to add a custom ip:port for your dApp.
I'll use an EC2 so my host is 0.0.0.0 and my example port is 7001.

```
{
  "name": "alpha-dapp",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "serve": "webpack-dev-server --config ./config/webpack.dev.js --host 0.0.0.0 --port 7001 --progress --colors --open",
    "build": "webpack --config ./config/webpack.prod.js -p --progress --colors",
    "build-analyze": "webpack --config ./config/webpack.prod-analyze.js -p --progress --colors",
    "serve-dist": "node scripts/serveDist.js",
    "deploy": "node scripts/deploy.js alpha.singularitynet.io us-east-1"
  },
  "repository": {
  ...
```
Now you have to install all the dependencies of the project and then run it.
From `alpha-dapp` folder.

```
$ npm install
```

And...
```
$ npm run serve
```












