class Resource:
    def __init__(self, name, initial_cost):
        self.name = name
        self.initial_cost = initial_cost
        self.cost = initial_cost

    def update_cost(self, new_cost):
        self.cost = new_cost

class Company:
    def __init__(self, name, initial_capital):
        self.name = name
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.resources = []

    def add_resource(self, resource):
        self.resources.append(resource)

    def update_resource_cost(self, resource_name, new_cost):
        for resource in self.resources:
            if resource.name == resource_name:
                resource.update_cost(new_cost)
                break

    def calculate_cost(self, resource_name):
        for resource in self.resources:
            if resource.name == resource_name:
                return resource.cost
        return None

    def manage_capital(self, cost_change):
        self.capital += cost_change
        if self.capital < 0:
            self.capital = 0

class Economy:
    def __init__(self, resources, companies):
        self.resources = resources
        self.companies = companies

    def update_company_capital(self, company_name, cost_change):
        for company in self.companies:
            if company.name == company_name:
                company.manage_capital(cost_change)
                break

    def update_resource_cost(self, resource_name, new_cost):
        for resource in self.resources:
            if resource.name == resource_name:
                resource.update_cost(new_cost)
                break

    def calculate_company_cost(self, company_name):
        total_cost = 0
        for resource in self.resources:
            if resource in company.resources:
                total_cost += resource.cost
        return total_cost

# Örnek resourceler ve şirketler
resource1 = Resource("CPU", 1000)
resource2 = Resource("RAM", 500)
resource3 = Resource("Storage", 2000)
resource4 = Resource("Power", 1500)

company1 = Company("TechCo", 5000)
company1.add_resource(resource1)
company1.add_resource(resource2)

company2 = Company("HealthTech", 3000)
company2.add_resource(resource3)
company2.add_resource(resource4)

economy = Economy([resource1, resource2, resource3, resource4], [company1, company2])

# Döngü algoritması
for i in range(10):
    # Random bir şirket ve resource seçimi
    company = economy.companies[i % 2]
    resource = economy.resources[i % 3]
    
    # Random bir değişim (cost_change) seçimi
    cost_change = 100 + 50 * i
    
    # Random bir değişim (cost_change) seçimi
    cost_change = 100 + 50 * i
    
    # Döngü algoritması: şirket kapasitesini değiştirmek
    economy.update_company_capital(company.name, cost_change)

    # Döngü algoritması: resource birimlerini değiştirmek
    economy.update_resource_cost(resource.name, resource.initial_cost + 100 + 50 * i)

    # Döngü algoritması: şirket ve resource bilgilerini yazdırmak
    print(f"Company: {company.name}, Capital: {company.capital}, Resources: {company.resources}")
    print(f"Resource: {resource.name}, Cost: {resource.cost}")
    print("---")

