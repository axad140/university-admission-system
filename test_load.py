from locust import HttpUser, task, between

class AdmissionUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def apply_load(self):
        # Testing 10,000 users simulation
        self.client.post("/submit_application", json={
            "name": "Test User",
            "email": "test@test.com",
            "marks": 950
        })

    @task
    def check_merit(self):
        self.client.get("/admin/merit_list")