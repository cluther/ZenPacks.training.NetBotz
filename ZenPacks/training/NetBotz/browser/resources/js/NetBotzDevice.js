Ext.onReady(function() {
    var DEVICE_OVERVIEW_ID = 'deviceoverviewpanel_summary';
    Ext.ComponentMgr.onAvailable(DEVICE_OVERVIEW_ID, function(){
        var overview = Ext.getCmp(DEVICE_OVERVIEW_ID);
        overview.removeField('memory');

        overview.addField({
            name: 'temp_sensor_count',
            fieldLabel: _t('# Temperature Sensors')
        });
    });
});

(function(){

var ZC = Ext.ns('Zenoss.component');

Ext.apply(Zenoss.render, {
    NetBotz_entityLinkFromGrid: function(obj, col, record) {
        if (!obj)
            return;

        if (typeof(obj) == 'string')
            obj = record.data;

        if (!obj.title && obj.name)
            obj.title = obj.name;

        var isLink = false;

        if (this.refName == 'componentgrid') {
            // Zenoss >= 4.2 / ExtJS4
            if (this.subComponentGridPanel || this.componentType != obj.meta_type)
                isLink = true;
        } else {
            // Zenoss < 4.2 / ExtJS3
            if (!this.panel || this.panel.subComponentGridPanel)
                isLink = true;
        }

        if (isLink) {
            return '<a href="javascript:Ext.getCmp(\'component_card\').componentgrid.jumpToEntity(\''+obj.uid+'\', \''+obj.meta_type+'\');">'+obj.title+'</a>';
        } else {
            return obj.title;
        }
    },
});

ZC.NetBotzComponentGridPanel = Ext.extend(ZC.ComponentGridPanel, {
    subComponentGridPanel: false,

    jumpToEntity: function(uid, meta_type) {
        var tree = Ext.getCmp('deviceDetailNav').treepanel;
        var tree_selection_model = tree.getSelectionModel();
        var components_node = tree.getRootNode().findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.text == 'Components';
                }

                // Zenoss < 4.2 / ExtJS3
                return n.text == 'Components';
            });

        // Reset context of component card.
        var component_card = Ext.getCmp('component_card');

        if (components_node.data) {
            // Zenoss >= 4.2 / ExtJS4
            component_card.setContext(components_node.data.id, meta_type);
        } else {
            // Zenoss < 4.2 / ExtJS3
            component_card.setContext(components_node.id, meta_type);
        }

        // Select chosen row in component grid.
        component_card.selectByToken(uid);

        // Select chosen component type from tree.
        var component_type_node = components_node.findChildBy(
            function(n) {
                if (n.data) {
                    // Zenoss >= 4.2 / ExtJS4
                    return n.data.id == meta_type;
                }

                // Zenoss < 4.2 / ExtJS3
                return n.id == meta_type;
            });

        if (component_type_node.select) {
            tree_selection_model.suspendEvents();
            component_type_node.select();
            tree_selection_model.resumeEvents();
        } else {
            tree_selection_model.select([component_type_node], false, true);
        }
    }
});


ZC.registerName('NetBotzEnclosure', _t('Enclosure'), _t('Enclosures'));

ZC.NetBotzEnclosurePanel = Ext.extend(ZC.NetBotzComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'NetBotzEnclosure',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'ASC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'enclosure_status'},
                {name: 'error_status'},
                {name: 'parent_id'},
                {name: 'docked_id'},
                {name: 'temperature_sensor_count'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                id: 'enclosure_status',
                dataIndex: 'enclosure_status',
                header: _t('Enclosure Status'),
                sortable: true,
                width: 120
            },{
                id: 'error_status',
                dataIndex: 'error_status',
                header: _t('Error Status'),
                sortable: true,
                width: 85
            },{
                id: 'parent_id',
                dataIndex: 'parent_id',
                header: _t('Enclosure'),
                sortable: true,
                width: 110
            },{
                id: 'docked_id',
                dataIndex: 'docked_id',
                header: _t('Docked To'),
                sortable: true,
                width: 110
            },{
                id: 'temperature_sensor_count',
                dataIndex: 'temperature_sensor_count',
                header: _t('# Temp Sensors'),
                sortable: true,
                width: 110
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.NetBotzEnclosurePanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('NetBotzEnclosurePanel', ZC.NetBotzEnclosurePanel);


Zenoss.nav.appendTo('Component', [{
    id: 'component_temperaturesensors',
    text: _t('Temperature Sensors'),
    xtype: 'NetBotzTemperatureSensorPanel',
    subComponentGridPanel: true,
    filterNav: function(navpanel) {
        // Only show this menu option when a component with the following meta_type is selected.
        if (navpanel.refOwner.componentType == 'NetBotzEnclosure') {
            return true;
        } else {
            return false;
        }
    },
    setContext: function(uid) {
        ZC.NetBotzTemperatureSensorPanel.superclass.setContext.apply(this, [uid]);
    }
}]);


ZC.registerName('NetBotzTemperatureSensor', _t('Temperature Sensor'), _t('Temperature Sensors'));

ZC.NetBotzTemperatureSensorPanel = Ext.extend(ZC.NetBotzComponentGridPanel, {
    constructor: function(config) {
        config = Ext.applyIf(config||{}, {
            componentType: 'NetBotzTemperatureSensor',
            autoExpandColumn: 'name',
            sortInfo: {
                field: 'name',
                direction: 'ASC'
            },
            fields: [
                {name: 'uid'},
                {name: 'name'},
                {name: 'meta_type'},
                {name: 'status'},
                {name: 'severity'},
                {name: 'usesMonitorAttribute'},
                {name: 'monitor'},
                {name: 'monitored'},
                {name: 'locking'},
                {name: 'enclosure'},
                {name: 'port'}
            ],
            columns: [{
                id: 'severity',
                dataIndex: 'severity',
                header: _t('Events'),
                renderer: Zenoss.render.severity,
                sortable: true,
                width: 50
            },{
                id: 'name',
                dataIndex: 'name',
                header: _t('Name'),
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                sortable: true
            },{
                id: 'enclosure',
                dataIndex: 'enclosure',
                header: _t('Enclosure ID'),
                sortable: true,
                renderer: Zenoss.render.NetBotz_entityLinkFromGrid,
                width: 150
            },{
                id: 'port',
                dataIndex: 'port',
                header: _t('Port ID'),
                sortable: true,
                width: 120
            },{
                id: 'monitored',
                dataIndex: 'monitored',
                header: _t('Monitored'),
                renderer: Zenoss.render.checkbox,
                sortable: true,
                width: 70
            },{
                id: 'locking',
                dataIndex: 'locking',
                header: _t('Locking'),
                renderer: Zenoss.render.locking_icons,
                width: 65
            }]
        });

        ZC.NetBotzTemperatureSensorPanel.superclass.constructor.call(
            this, config);
    }
});

Ext.reg('NetBotzTemperatureSensorPanel', ZC.NetBotzTemperatureSensorPanel);

})();
