# MINI_PROJECT — Port the catalog API cloud-native

Take the lab-05 (`oracle-apex/05-restful-services`) product-catalog API
(or any Spring Boot CRUD service):

1. Containerize with the layered non-root Dockerfile from CODE_DEEP_DIVE
   (MaxRAMPercentage, probes enabled, env-only config).
2. Run at 512 MB and 2 GB limits; tune f per limit using the memory math;
   record OOM-free sustained load in both.
3. Build a second native-image (or CRaC) variant; cold-start both 20×;
   publish the startup/memory table with the winner per profile.
4. Deploy to *one* of AWS/GCP/Azure (labs 54–56) with health-gated rollout
   and secret-manager wiring; capture traces end-to-end.

Deliverable: repo + one-page economics note (which runtime where, why).
