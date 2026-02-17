import random
import datetime
from django.core.management.base import BaseCommand
from apps.home.models import (
    Station, L_Station, I_Station,
    Route, L_Route, I_Route,
    Train_Model, Train, S_Series, A_Series,
    Trip, L_Trip, I_Trip
)

class Command(BaseCommand):
    help = 'Seeds the database with comprehensive Narnia-themed Tirian Trains data'

    def handle(self, *args, **kwargs):
        self.stdout.write("Initializing Tirian Trains Database Generation...")

        try:
            # ---------------------------------------------------------
            # 1. TRAIN MODELS
            # ---------------------------------------------------------
            self.stdout.write("Creating Train Models...")
            model_s, _ = Train_Model.objects.get_or_create(
                model_name="S-001", defaults={'max_speed': 80, 'seat_capacity': 100, 'toilet_capacity': 2}
            )
            model_a, _ = Train_Model.objects.get_or_create(
                model_name="A-001", defaults={'max_speed': 150, 'seat_capacity': 60, 'toilet_capacity': 4, 'has_reclining_seats': True, 'has_luggage_storage': True}
            )

            # ---------------------------------------------------------
            # 2. TRAINS
            # ---------------------------------------------------------
            self.stdout.write("Creating Trains...")
            s_trains = []
            for i in range(1, 4):
                train, _ = Train.objects.get_or_create(
                    train_id=f"10000{i}", defaults={'train_number': f"S100{i}", 'train_series': 'S', 'train_model': model_s}
                )
                s_series, _ = S_Series.objects.get_or_create(train=train)
                s_trains.append(s_series)

            a_trains = []
            for i in range(1, 4):
                train, _ = Train.objects.get_or_create(
                    train_id=f"20000{i}", defaults={'train_number': f"A200{i}", 'train_series': 'A', 'train_model': model_a, 'has_food_service': True}
                )
                a_series, _ = A_Series.objects.get_or_create(train=train)
                a_trains.append(a_series)

            # ---------------------------------------------------------
            # 3. STATIONS
            # ---------------------------------------------------------
            self.stdout.write("Creating Stations...")
            local_station_names = ["Lantern Waste", "Beaversdam", "Beruna", "Dancing Lawn", "Aslan's How", "Cair Paravel (Local)"]
            l_stations = []
            for idx, name in enumerate(local_station_names):
                st, _ = Station.objects.get_or_create(station_id=f"30000{idx+1}", defaults={'station_name': name, 'station_type': 'L'})
                l_st, _ = L_Station.objects.get_or_create(l_station_id=st)
                l_stations.append(l_st)

            inter_station_names = ["Cair Paravel (Inter)", "Anvard", "Tashbaan", "Azim Balda", "Mezreel"]
            i_stations = []
            for idx, name in enumerate(inter_station_names):
                st, _ = Station.objects.get_or_create(station_id=f"40000{idx+1}", defaults={'station_name': name, 'station_type': 'I'})
                i_st, _ = I_Station.objects.get_or_create(i_station_id=st)
                i_stations.append(i_st)

            # ---------------------------------------------------------
            # 4. ROUTES (Connecting stations in both directions)
            # ---------------------------------------------------------
            self.stdout.write("Creating Routes...")
            l_routes = []
            route_id_counter = 500001
            for i in range(len(l_stations) - 1):
                # Forward Route (e.g., Lantern Waste -> Beaversdam)
                rt, _ = Route.objects.get_or_create(route_id=str(route_id_counter), defaults={'route_type': 'L'})
                l_rt, _ = L_Route.objects.get_or_create(l_route_id=rt, defaults={'l_route_origin': l_stations[i], 'l_route_desti': l_stations[i+1]})
                l_routes.append(l_rt)
                route_id_counter += 1
                
                # Backward Route (e.g., Beaversdam -> Lantern Waste)
                rt_rev, _ = Route.objects.get_or_create(route_id=str(route_id_counter), defaults={'route_type': 'L'})
                l_rt_rev, _ = L_Route.objects.get_or_create(l_route_id=rt_rev, defaults={'l_route_origin': l_stations[i+1], 'l_route_desti': l_stations[i]})
                l_routes.append(l_rt_rev)
                route_id_counter += 1

            i_routes = []
            route_id_counter = 600001
            for i in range(len(i_stations) - 1):
                # Forward Route
                rt, _ = Route.objects.get_or_create(route_id=str(route_id_counter), defaults={'route_type': 'I'})
                i_rt, _ = I_Route.objects.get_or_create(i_route_id=rt, defaults={'i_route_origin': i_stations[i], 'i_route_desti': i_stations[i+1]})
                i_routes.append(i_rt)
                route_id_counter += 1
                
                # Backward Route
                rt_rev, _ = Route.objects.get_or_create(route_id=str(route_id_counter), defaults={'route_type': 'I'})
                i_rt_rev, _ = I_Route.objects.get_or_create(i_route_id=rt_rev, defaults={'i_route_origin': i_stations[i+1], 'i_route_desti': i_stations[i]})
                i_routes.append(i_rt_rev)
                route_id_counter += 1

            # ---------------------------------------------------------
            # 5. TRIPS
            # ---------------------------------------------------------
            self.stdout.write("Creating Scheduled Trips...")
            today = datetime.date.today()
            trip_counter = 1

            # Generate trips for today and the next 2 days
            for day_offset in range(3):
                current_date = today + datetime.timedelta(days=day_offset)

                # Local Trips (45 mins duration)
                for l_route in l_routes:
                    for _ in range(2): # 2 trips per route, per day
                        hour = random.randint(6, 20)
                        minute = random.choice([0, 15, 30, 45])
                        dep_time = datetime.time(hour, minute)
                        arr_dt = datetime.datetime.combine(current_date, dep_time) + datetime.timedelta(minutes=45)
                        
                        train = random.choice(s_trains)
                        trip_id_str = f"{current_date.strftime('%Y%m%d')}L{trip_counter:03d}"
                        
                        trip, _ = Trip.objects.get_or_create(
                            trip_id=trip_id_str,
                            defaults={
                                'route': l_route.l_route_id, 'train': train.train,
                                'departure_time': dep_time, 'arrival_time': arr_dt.time(),
                                'schedule_day': current_date, 'trip_cost': random.choice([15, 20, 25]),
                                'trip_type': 'L'
                            }
                        )
                        L_Trip.objects.get_or_create(l_trip_id=trip, defaults={'s_train': train, 'l_route': l_route})
                        trip_counter += 1

                # Inter-town Trips (2 hours duration)
                for i_route in i_routes:
                    for _ in range(2): # 2 trips per route, per day
                        hour = random.randint(5, 21)
                        minute = random.choice([0, 30])
                        dep_time = datetime.time(hour, minute)
                        arr_dt = datetime.datetime.combine(current_date, dep_time) + datetime.timedelta(hours=2)
                        
                        train = random.choice(a_trains)
                        trip_id_str = f"{current_date.strftime('%Y%m%d')}I{trip_counter:03d}"
                        
                        trip, _ = Trip.objects.get_or_create(
                            trip_id=trip_id_str,
                            defaults={
                                'route': i_route.i_route_id, 'train': train.train,
                                'departure_time': dep_time, 'arrival_time': arr_dt.time(),
                                'schedule_day': current_date, 'trip_cost': random.choice([50, 75, 100]),
                                'trip_type': 'I'
                            }
                        )
                        I_Trip.objects.get_or_create(i_trip_id=trip, defaults={'a_train': train, 'i_route': i_route})
                        trip_counter += 1

            self.stdout.write(self.style.SUCCESS(f"Successfully seeded Database with {trip_counter-1} Scheduled Trips!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error seeding data: {e}"))