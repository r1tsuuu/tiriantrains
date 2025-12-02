from django.contrib import admin
from .models import (Customer, Trip, Ticket, Station, Route, Train, 
    Crew_In_Charge, Maintenance_Log, Train_Model, Task,
    L_Station, I_Station, L_Route, I_Route, 
    S_Series, A_Series, L_Trip, I_Trip, Log_Task
)

class StationAdmin(admin.ModelAdmin):
    """
    Admin view for Station model.
    """
    list_display = ('station_id', 'station_name', 
                    'station_type')
    list_filter = ('station_type',)


class L_StationAdmin(admin.ModelAdmin):
    list_display = ('l_station_id', 'get_name')
    def get_name(self, obj):
        return obj.l_station_id.station_name
    get_name.short_description = 'Station Name'


class I_StationAdmin(admin.ModelAdmin):
    list_display = ('i_station_id', 'get_name')
    def get_name(self, obj):
        return obj.i_station_id.station_name
    get_name.short_description = 'Station Name'


class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_id', 'route_type')
    list_filter = ('route_type',)


class L_RouteAdmin(admin.ModelAdmin):
    list_display = ('l_route_id', 'l_route_origin', 'l_route_desti')
    def get_origin_name(self, obj):
        # Navigates: L_Route -> L_Station -> Station -> Name
        return obj.l_route_origin.l_station_id.station_name
    get_origin_name.short_description = 'Origin'

    def get_dest_name(self, obj):
        return obj.l_route_desti.l_station_id.station_name
    get_dest_name.short_description = 'Destination'

class I_RouteAdmin(admin.ModelAdmin):
    list_display = ('i_route_id', 'i_route_origin', 'i_route_desti')
    def get_origin_name(self, obj):
        # Navigates: I_Route -> I_Station -> Station -> Name
        return obj.i_route_origin.i_station_id.station_name
    get_origin_name.short_description = 'Origin'

    def get_dest_name(self, obj):
        return obj.i_route_desti.i_station_id.station_name
    get_dest_name.short_description = 'Destination'


class Train_ModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'max_speed', 'seat_capacity')


class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_id', 'train_number', 'train_series', 'train_model')
    list_filter = ('train_series', 'has_food_service')


class S_SeriesAdmin(admin.ModelAdmin):
    list_display = ('train',)


class A_SeriesAdmin(admin.ModelAdmin):
    list_display = ('train',)


class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_id', 'route',
                    'train', 'schedule_day', 
                    'departure_time', 'arrival_time',
                    'trip_type', 'trip_cost')
    list_filter = ('trip_type', 'schedule_day')


class L_TripAdmin(admin.ModelAdmin):
    list_display = ('l_trip_id', 's_train', 'l_route')


class I_TripAdmin(admin.ModelAdmin):
    list_display = ('i_trip_id', 'a_train', 'i_route')


class CustomerAdmin(admin.ModelAdmin):
    """
    Admin view for Customer model.
    """
    list_display = ('user','customer_id',
                    'last_name','given_name',
                     'middle_initial', 'birth_date', 
                    'gender')
    search_fields = ('customer_id', 'last_name')
    

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'customer',
                    'purchase_date', 'trip_date', 
                    'total_cost')
    read_only_fields = ('ticket_id', 'total_cost')
    filter_horizontal = ('trips',)


class CrewInChargeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'first_initial', 'last_name')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name',)


class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'date', 
                    'train', 'crew_in_charge', 
                    'condition')
    read_only_fields = ('log_id',)
    list_filter = ('condition', 'date')


class LogTaskAdmin(admin.ModelAdmin):
    list_display = ('log', 'task')
    

admin.site.register(Station, StationAdmin)
admin.site.register(L_Station, L_StationAdmin)
admin.site.register(I_Station, I_StationAdmin)

admin.site.register(Route, RouteAdmin)
admin.site.register(L_Route, L_RouteAdmin)
admin.site.register(I_Route, I_RouteAdmin)

admin.site.register(Train_Model, Train_ModelAdmin)
admin.site.register(Train, TrainAdmin)
admin.site.register(S_Series, S_SeriesAdmin)
admin.site.register(A_Series, A_SeriesAdmin)

admin.site.register(Trip, TripAdmin)
admin.site.register(L_Trip, L_TripAdmin)
admin.site.register(I_Trip, I_TripAdmin)

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Ticket, TicketAdmin)

admin.site.register(Crew_In_Charge, CrewInChargeAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Maintenance_Log, MaintenanceLogAdmin)
admin.site.register(Log_Task, LogTaskAdmin)