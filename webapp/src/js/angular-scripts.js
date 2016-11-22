"use strict";

const angular = require('angular');

const app = angular.module("app", [require('angular-route'), require('ng-infinite-scroll')]);

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
      $location.path("/");
      return;
    }

    let session = {
      name: data.name,
      username: data.username,
      authenticated: true
    };

    sessionService.setSession(session);

    $scope.session = session;
    $location.path("/profile");

  }).error(function() {
    console.log("Error occured while getting login");
  });

  $scope.logout = function() {
    $http.post('logout', {}).success(function() {
      sessionService.resetSession();
      $scope.session = {};
      $location.path("/");
    }).error(function(data) {
      sessionService.resetSession();
      $location.path("/");
    });
  };

});

app.controller("profileController", /*@ngInject*/function($scope, $location, $http, sessionService, Github) {
  let session = sessionService.getSession();
  $scope.session = session;

  $scope.github = new Github();

  $http.get("events").success(function(data) {

    if (data.error === true) {
      $location.path("/");
      return;
    }

    $scope.events = data;

  }).error(function() {
    console.log("Error occured while getting login");
  });
});

app.factory('Github', function($http) {
  const Github = function() {
    this.items = [];
    this.busy = false;
    this.page = 1;
    this.loader = false;
  };

  Github.prototype.nextPage = function() {

    if (this.busy) {
      return;
    }

    this.busy = true;
    this.loader = true;
    const url = `/events?page=${this.page}`;

    $http.get(url).success(function(data) {
      console.log(data);

      if (data.hasOwnProperty("error")  == true &&
          data.hasOwnProperty("type") == true &&
          data['type'] == 'END') {
        console.log("here");
        this.busy = true;
        this.loader = false;
        return;
      }
      
      let items = data;

      for (let i = 0; i < items.length; i++) {
        this.items.push(items[i]);
      }

      this.page = this.page + 1;
      this.busy = false;
      this.loader = false;
    }.bind(this)).error(function() {
      this.busy = true;
      this.loader = false;
    }.bind(this));
  };

  return Github;
});
