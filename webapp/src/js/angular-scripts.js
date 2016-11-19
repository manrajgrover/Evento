"use strict";

const angular = require('angular');

const app = angular.module("app", [require('angular-route')]);

app.config(function($httpProvider) {
  $httpProvider.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
});

app.config(/*@ngInject*/function($routeProvider) {
  $routeProvider.when('/', {
    controller: 'homeController',
    templateUrl: 'dist/views/home.html'
  }).when('/profile', {
    controller: 'profileController',
    templateUrl: 'dist/views/profile.html'
  }).otherwise({
    redirectTo: '/'
  });
});

app.service('sessionService', function() {
  let session = {};

  return {
    resetSession: function() {
      session = {};
    },
    getSession : function() {
      return session;
    },
    setSession : function(_session) {
      session = _session;
    }
  }
});

app.run(/*@ngInject*/function($rootScope, $timeout, $location, sessionService){

  $rootScope.stateIsLoading = false;
  $rootScope.$on( "$routeChangeStart", function(event, next, current) {
    $rootScope.stateIsLoading = true;
    let session = sessionService.getSession();
    if (!session.hasOwnProperty('authenticated') || session.authenticated === false) {
      if ( next.templateUrl !== "dist/views/home.html" ) {
        $location.path( "/" );
      }
    }
  });

  $rootScope.$on('$routeChangeSuccess', function() {
    $timeout(function() {
      $rootScope.stateIsLoading = false;
      console.log("Hello stopping");
    }, 2000);
  });

  $rootScope.$on('$routeChangeError', function() {
    console.log("Error");
  });

});


app.controller("homeController", /*@ngInject*/function($scope) {

  $scope.login = () => {
    window.location.replace("login");
  }

});

app.controller("navController", /*@ngInject*/function($scope, $http, $location, sessionService) {

  angular.element(document).ready(function () {
    jQuery(".dropdown-toggle").dropdown();
  });

  $http.get("login").success(function(data) {

    if (data.error === true) {
      return;
    }

    let session = {
      name: data.name,
      email: data.email,
      username: data.username,
      authenticated: true
    };

    sessionService.setSession(session);

    $scope.session = session;
    $location.path("/profile");

  }).error(function() {
    //self.authenticated = false;
  });

  $scope.logout = function() {
    $http.post('logout', {}).success(function() {
      sessionService.resetSession();
      $scope.session = {};
      $location.path("/");
    }).error(function(data) {
      self.authenticated = false;
      $location.path("/");
    });
  };

});

app.controller("profileController", /*@ngInject*/function($scope, $location, $http, sessionService) {
  let session = sessionService.getSession();
  $scope.session = session;
});
