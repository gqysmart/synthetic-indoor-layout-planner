from __future__ import annotations

from datetime import datetime
from airflow.sdk import dag, task




from my_app.backend.planner.layout_csp  import (
    load_room_data,
    random_place_furnitures,
    enforce_csp,
)

@dag(
    dag_id="room_layout_csp_dag",
    start_date=datetime(2025, 1, 1),
    schedule=None,
    catchup=False,
)
def room_layout_csp_dag():

    @task()
    def t_load_room():
        return load_room_data()

    @task()
    def t_random_layout(data):
        return random_place_furnitures(data)

    @task()
    def t_enforce_csp(state):
        return enforce_csp(state)

    @task()
    def t_display(result):
        print(result)

    data = t_load_room()
    init_state = t_random_layout(data)
    final_state = t_enforce_csp(init_state)
    t_display(final_state)




room_layout_csp_dag()
