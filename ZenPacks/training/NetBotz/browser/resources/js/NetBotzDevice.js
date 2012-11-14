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

ZC.registerName('NetBotzTemperatureSensor', _t('Temperature Sensor'), _t('Temperature Sensors'));

ZC.NetBotzTemperatureSensorPanel = Ext.extend(ZC.ComponentGridPanel, {
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
                sortable: true
            },{
                id: 'enclosure',
                dataIndex: 'enclosure',
                header: _t('Enclosure ID'),
                sortable: true,
                width: 120
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
