# Flashcards — JPMS

| Q | A |
|---|---|
| module-info.java? | Module declaration file |
| module name? | Reverse-DNS, e.g. com.app |
| requires m? | Depends on m |
| requires transitive? | Re-export dep |
| requires static? | Optional at run |
| exports p? | Public API package |
| exports p to m? | Qualified export |
| opens p? | Reflective access |
| opens p to m? | Qualified open |
| open module? | All pkgs open |
| uses S? | Consume service S |
| provides S with I? | Implement service |
| ServiceLoader.load? | Discover providers |
| Split package? | Error, same pkg 2 mods |
| Automatic module? | Jar w/o info on path |
| Unnamed module? | Classpath code |
| Boot layer? | Startup modules |
| Child layer? | defineModulesWithOneLoader |
| --module-path? | -p modules location |
| -m mod/cls? | Run module main |
| --describe-module? | Show module33 meta |
| --add-modules? | Add root mods |
| --add-exports? | Export at CLI |
| --add-opens? | Open at CLI |
| --add-reads? | Add readability edge |
| jdeps -s? | Summary deps |
| jdeps --gen-info? | Generate module-info |
| jlink add-modules? | Roots for image |
| strip-debug? | Smaller image |
| compress=2? | Zip compress image |
| no-header-files? | Drop headers |
| Image size JDK? | ~300MB → ~40MB |
| readability? | m reads n edge |
| accessibility? | Exported+readable |
| Encapsulation? | Non-export hidden |
| Reflection break? | Needs opens |
| Deep reflect? | setAccessible+opens |
| Maven mod plugin? | moditect/add config |
| Gradle modules? | module-info in src |
| Test w/ modules? | patch-module for tests |
| --patch-module? | Overlay test classes |
| Layer parent? | Boot or custom |
| OneLoader? | Single loader layer |
| Many loaders? | One per module |
| Service in layer? | Uses/provides wiring |
| Plugin unload? | Drop layer ref |
| Versionless? | No vers in JPMS |
| Jar hell fix? | Explicit requires |
| Classpath mode? | All unnamed |
| Migrate order? | Leaves first |
| Top-down? | App last |
| Bottom-up? | Libs first |
| jdeps missing? | Not found deps |
| internal API? | jdk.internal hidden |
| jdk.unsupported? | Unsafe escape |
| --illegal-access? | Legacy flag (removed) |
| Strong encap? | Default since 17 |
| Main in module? | -m mod/pkg.Main |
| Multi-release? | MR jar + modules |
| Modular jar? | Jar with module-info |
| Locate image java? | img/bin/java |
| Health check? | java --list-modules |
| Best practice? | Export minimal API |
| Worst smell? | open module + all exports |
| Debug reads? | --show-module-resolution |
| Resolution? | Resolve root closure |
| Missing service? | Empty loader list |
