from pxr import Usd, UsdPhysics, Gf
import numpy as np

stage = Usd.Stage.Open("c:/Users/rcrym/Documents/SimpleDogUSDOnlyDogNoDrives/Assembly_1_base.usd")

print("=== MASS PROPERTIES ===")
for prim in stage.Traverse():
    if prim.HasAPI(UsdPhysics.MassAPI):
        mass_api = UsdPhysics.MassAPI(prim)
        mass = mass_api.GetMassAttr().Get()
        
        # Check for crazy values
        if mass and mass > 0:
            print(f"\n{prim.GetPath().name}:")
            print(f"  Mass: {mass:.4f} kg")
            
            # Check inertia if present
            diag = mass_api.GetDiagonalInertiaAttr().Get()
            if diag:
                print(f"  Inertia diagonal: {diag}")
                # Red flag: any value > 10x the mass is suspicious
                if any(abs(d) > mass * 10 for d in diag):
                    print("  ⚠️  WARNING: Inertia seems too high!")

print("\n=== CHECKING FOOT COLLISIONS ===")
# Check if feet have collision
foot_names = ["FL_calf", "FR_calf", "RL_calf", "RR_calf"]
for prim in stage.Traverse():
    if any(foot in prim.GetPath().pathString for foot in foot_names):
        if prim.HasAPI(UsdPhysics.CollisionAPI):
            print(f"✓ {prim.GetPath().name} has collision")