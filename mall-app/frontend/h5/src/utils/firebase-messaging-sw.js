importScripts('https://www.gstatic.com/firebasejs/8.2.7/firebase-app.js');
importScripts('https://www.gstatic.com/firebasejs/8.2.7/firebase-messaging.js');

// Initialize the Firebase app in the service worker by passing the generated config
var firebaseConfig = {
    apiKey: "AIzaSyCAfTDznXqUGIw8odfEwVgmCg_2KwWnRps",
    authDomain: "fir-eb636.firebaseapp.com",
    projected: "fir-eb636",
    projectId: "fir-eb636",
    storageBucket: "fir-eb636.appspot.com",
    messagingSenderId: "270054984552",
    appId: "1:270054984552:web:cdf4559c94bac0e24d64dd",
    measurementId: "G-T6XQDEYV5R",
    databaseURL: '270054984552'
};

firebase.initializeApp(firebaseConfig);

// Retrieve firebase messaging
const messaging = firebase.messaging();

messaging.onBackgroundMessage(function (payload) {
    console.log('Received background message ', payload);

    const notificationTitle = payload.notification.title;
    const notificationOptions = {
        body: payload.notification.body
    };

    self.registration.showNotification(notificationTitle,
        notificationOptions);
});