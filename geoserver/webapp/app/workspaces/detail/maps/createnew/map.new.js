angular.module('gsApp.workspaces.maps.new', [
  'ngSanitize',
  'gsApp.alertpanel',
  'gsApp.projfield',
  'gsApp.core.utilities',
  'ui.select',
  'ngGrid'
])
.controller('NewMapCtrl', ['$scope', '$state', '$stateParams', '$rootScope',
  '$log', 'GeoServer',
  function ($scope, $state, $stateParams, $rootScope, $log,
    GeoServer) {

    $scope.workspace = $stateParams.workspace;
    $scope.mapInfo = {
      'abstract': ''
    };
    $scope.selectedLayers = [];
    $scope.newMap = {};
    $scope.map = {};
    $scope.title = 'New Map';
    $scope.step = 1;

    $scope.crsTooltip =
      '<h5>Add a projection in EPSG</h5>' +
      '<p>Coordinate Reference System (CRS) info is available at ' +
        '<a href="http://prj2epsg.org/search" target="_blank">' +
          'http://prj2epsg.org' +
        '</a>' +
      '</p>';

    $scope.cancel = function() {
      $state.go('workspace.maps.main', {workspace:$scope.workspace});
    };

    $scope.createMap = function(layerSelections) {
      $scope.mapInfo.layers = [];
      for (var i=0; i< layerSelections.length; i++) {
        $scope.mapInfo.layers.push({
          'name': layerSelections[i].name,
          'workspace': $scope.workspace
        });
      }

      GeoServer.map.create($scope.workspace, $scope.mapInfo).then(
        function(result) {
          if (result.success) {
            $rootScope.alerts = [{
              type: 'success',
              message: 'Map ' + result.data.name + ' created  with ' +
                result.data.layers.length + ' layer(s).',
              fadeout: true
            }];
            $scope.maps.push(result.data);
          } else {
            $rootScope.alerts = [{
              type: 'danger',
              message: 'Could not create map.',
              fadeout: true
            }];
          }
        });
    }; // end createMap

    $scope.createNewLayers = function() {
      $state.go('workspace.data.import.file', {
        workspace: $scope.workspace,
        maps: [$scope.mapInfo]
      });
    };

    // Available Layers
    $scope.layers = [];
    $scope.totalServerItems = [];

    $scope.pagingOptions = {
      pageSizes: [25, 50, 100],
      pageSize: 25,
      currentPage: 1
    };
    $scope.filterOptions = {
        filterText: '',
        useExternalFilter: true
      };
    $scope.layerSelections = [];

    $scope.gridOptions = {
      data: 'layers',
      enableCellSelection: false,
      enableRowSelection: true,
      enableCellEdit: false,
      checkboxHeaderTemplate:
        '<input class="ngSelectionHeader" type="checkbox"' +
          'ng-model="allSelected" ng-change="toggleSelectAll(allSelected)"/>',
      int: function() {
        $log('done');
      },
      sortInfo: {fields: ['name'], directions: ['asc']},
      showSelectionCheckbox: true,
      selectWithCheckboxOnly: false,
      selectedItems: $scope.layerSelections,
      multiSelect: true,
      columnDefs: [
        {field: 'name', displayName: 'Layer', width: '20%'},
        {field: 'title',
          displayName: 'Title',
          enableCellEdit: true,
          cellTemplate:
            '<div class="grid-text-padding"' +
              'alt="{{row.entity.description}}"' +
              'title="{{row.entity.description}}">' +
              '{{row.entity.title}}' +
            '</div>',
          width: '20%'
        },
        {field: 'geometry',
          displayName: 'Type',
          cellClass: 'text-center',
          cellTemplate:
            '<div get-type ' +
              'geometry="{{row.entity.geometry}}">' +
            '</div>',
          width: '5%'
        },
        {field: 'srs',
          displayName: 'SRS',
          cellClass: 'text-center',
          cellTemplate:
            '<div class="grid-text-padding">' +
              '{{row.entity.proj.srs}}' +
            '</div>',
          width: '7%'
        },
        {field: 'settings',
          displayName: 'Settings',
          cellClass: 'text-center',
          sortable: false,
          cellTemplate:
            '<div ng-class="col.colIndex()">' +
              '<a ng-click="onStyleEdit(row.entity)">' +
                '<i class="fa fa-gear grid-icons" ' +
                  'alt="Edit Layer Settings" ' +
                  'title="Edit Layer Settings"></i>' +
              '</a>' +
            '</div>',
          width: '10%'
        }
      ],
      enablePaging: true,
      enableColumnResize: false,
      showFooter: true,
      totalServerItems: 'totalServerItems',
      pagingOptions: $scope.pagingOptions
    };

    $scope.loadLayers = function() {
      GeoServer.layers.get(
        $scope.workspace,
        $scope.pagingOptions.currentPage-1,
        $scope.pagingOptions.pageSize
      ).then(function(result) {
        if (result.success) {
          $scope.layers = result.data.layers;
          $scope.totalServerItems = result.data.total;
        } else {
          $rootScope.alerts = [{
            type: 'danger',
            message: 'Layers for workspace ' + $scope.workspace.name +
              ' could not be loaded.',
            fadeout: true
          }];
        }
      });
    };
    $scope.loadLayers();

    $scope.setMap = function(map) {
      $scope.selectedMap = map;
    };

    $scope.mapsToCreate = [$scope.mapInfo];

  }]);