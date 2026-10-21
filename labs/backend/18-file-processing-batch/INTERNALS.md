# Internals: Spring Batch

## JobLauncher
JobLauncher.start() creates a JobExecution, validates parameters, and delegates to Job.execute().

## SimpleStepHandler
Each Step is executed by SimpleStepHandler:
1. Create StepExecution
2. Open ItemStream (reader/writer)
3. Repeat: read chunk, process chunk, write chunk
4. Update execution context
5. Close ItemStream
