from django.contrib import admin
from .models import (Customer, Trip, Ticket, Station, Route, Train, 
    Crew_In_Charge, Maintenance_Log, Train_Model, Task,
    L_Station, I_Station, L_Route, I_Route, 
    S_Series, A_Series, L_Trip, I_Trip, Log_Task
)

# ------------------------------------------------------------------
# STATIONS & ROUTES
# ------------------------------------------------------------------
class StationAdmin(admin.ModelAdmin):
    list_display = ('station_id', 'station_name', 'station_type')
    list_filter = ('station_type',)
    search_fields = ('station_id', 'station_name')

class L_StationAdmin(admin.ModelAdmin):
    list_display = ('l_station_id', 'get_name')
    search_fields = ('l_station_id__station_name',)

    @admin.display(description='Station Name')
    def get_name(self, obj):
        return obj.l_station_id.station_name

class I_StationAdmin(admin.ModelAdmin):
    list_display = ('i_station_id', 'get_name')
    search_fields = ('i_station_id__station_name',)

    @admin.display(description='Station Name')
    def get_name(self, obj):
        return obj.i_station_id.station_name

class RouteAdmin(admin.ModelAdmin):
    list_display = ('route_id', 'origin', 'destination', 'route_type')
    list_filter = ('route_type',)
    search_fields = ('route_id',)

class L_RouteAdmin(admin.ModelAdmin):
    list_display = ('l_route_id', 'get_origin_name', 'get_dest_name')

    @admin.display(description='Origin')
    def get_origin_name(self, obj):
        return obj.l_route_origin.l_station_id.station_name

    @admin.display(description='Destination')
    def get_dest_name(self, obj):
        return obj.l_route_desti.l_station_id.station_name

class I_RouteAdmin(admin.ModelAdmin):
    list_display = ('i_route_id', 'get_origin_name', 'get_dest_name')

    @admin.display(description='Origin')
    def get_origin_name(self, obj):
        return obj.i_route_origin.i_station_id.station_name

    @admin.display(description='Destination')
    def get_dest_name(self, obj):
        return obj.i_route_desti.i_station_id.station_name

# ------------------------------------------------------------------
# TRAINS
# ------------------------------------------------------------------
class Train_ModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'max_speed', 'seat_capacity')
    search_fields = ('model_name',)
    # UI POLISH: Group fields visually into cards
    fieldsets = (
        ('Basic Specifications', {'fields': ('model_name', 'max_speed', 'seat_capacity', 'toilet_capacity')}),
        ('Amenities', {'fields': ('has_reclining_seats', 'has_folding_tables', 'has_disability_access', 'has_luggage_storage')}),
    )

class TrainAdmin(admin.ModelAdmin):
    list_display = ('train_number', 'train_id', 'train_series', 'train_model')
    list_filter = ('train_series', 'has_food_service', 'has_vending_machines')
    search_fields = ('train_number', 'train_id')
    fieldsets = (
        ('Identification', {'fields': ('train_id', 'train_number')}),
        ('Classification', {'fields': ('train_series', 'train_model')}),
        ('Services', {'fields': ('has_vending_machines', 'has_food_service')}),
    )

# ------------------------------------------------------------------
# TRIPS & TICKETS
# ------------------------------------------------------------------
class TripAdmin(admin.ModelAdmin):
    list_display = ('trip_id', 'route', 'train', 'schedule_day', 'departure_time', 'arrival_time', 'trip_cost', 'trip_type')
    list_filter = ('trip_type', 'is_archived')
    search_fields = ('trip_id', 'route__route_id', 'train__train_number')
    
    date_hierarchy = 'schedule_day' 
    
    fieldsets = (
        ('Trip Identification', {'fields': ('trip_id', 'trip_type', 'is_archived')}),
        ('Schedule details', {'fields': ('schedule_day', 'departure_time', 'arrival_time', 'duration')}),
        ('Assignments', {'fields': ('route', 'train')}),
        ('Pricing', {'fields': ('trip_cost',)}),
    )
    readonly_fields = ('duration',) # Auto-calculated, so prevent manual edits

class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_id', 'customer', 'purchase_date', 'trip_date', 'total_cost')
    search_fields = ('ticket_id', 'customer__last_name', 'customer__customer_id')
    list_filter = ('purchase_date', 'trip_date')
    date_hierarchy = 'purchase_date'
    filter_horizontal = ('trips',)
    
    fieldsets = (
        ('Ticket Information', {'fields': ('ticket_id', 'customer', 'total_cost')}),
        ('Dates', {'fields': ('purchase_date', 'trip_date')}),
        ('Itinerary', {'fields': ('trips',)}),
    )
    readonly_fields = ('ticket_id', 'total_cost')

class CustomerAdmin(admin.ModelAdmin):
    list_display = ('customer_id', 'last_name', 'given_name', 'user', 'gender')
    search_fields = ('customer_id', 'last_name', 'given_name', 'user__username')
    list_filter = ('gender',)
    
    fieldsets = (
        ('System Account', {'fields': ('user', 'customer_id')}),
        ('Personal Information', {'fields': ('given_name', 'middle_initial', 'last_name', 'birth_date', 'gender')}),
        ('Media', {'fields': ('profile_picture',)}),
    )
    readonly_fields = ('customer_id',)

# ------------------------------------------------------------------
# MAINTENANCE
# ------------------------------------------------------------------
class CrewInChargeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'last_name', 'first_initial')
    search_fields = ('employee_id', 'last_name')

# NEW: Create an Inline editor for Tasks
class LogTaskInline(admin.TabularInline):
    model = Log_Task
    extra = 1 # Shows one blank row by default to quickly add a new task

class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('log_id', 'date', 'train', 'crew_in_charge', 'condition')
    list_filter = ('condition', 'date')
    search_fields = ('log_id', 'train__train_number', 'crew_in_charge__last_name')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Log Information', {'fields': ('log_id', 'date', 'condition')}),
        ('Assignments', {'fields': ('train', 'crew_in_charge')}),
    )
    readonly_fields = ('log_id',)
    inlines = [LogTaskInline]

# ------------------------------------------------------------------
# BASE ADMIN REGISTRATIONS
# ------------------------------------------------------------------
admin.site.register(Station, StationAdmin)
admin.site.register(L_Station, L_StationAdmin)
admin.site.register(I_Station, I_StationAdmin)

admin.site.register(Route, RouteAdmin)
admin.site.register(L_Route, L_RouteAdmin)
admin.site.register(I_Route, I_RouteAdmin)

admin.site.register(Train_Model, Train_ModelAdmin)
admin.site.register(Train, TrainAdmin)
admin.site.register(S_Series) 
admin.site.register(A_Series)

admin.site.register(Trip, TripAdmin)
admin.site.register(L_Trip)
admin.site.register(I_Trip)

admin.site.register(Customer, CustomerAdmin)
admin.site.register(Ticket, TicketAdmin)

admin.site.register(Crew_In_Charge, CrewInChargeAdmin)
admin.site.register(Task)
admin.site.register(Maintenance_Log, MaintenanceLogAdmin)
admin.site.register(Log_Task)