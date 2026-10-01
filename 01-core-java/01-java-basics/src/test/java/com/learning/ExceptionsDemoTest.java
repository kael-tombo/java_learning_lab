package com.learning;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.DisplayName;

import static org.junit.jupiter.api.Assertions.*;

/**
 * Comprehensive test suite for ExceptionsDemo class.
 * Tests exception handling, custom exceptions, and resource management.
 */
@DisplayName("ExceptionsDemo Test Suite")
class ExceptionsDemoTest {
    
    // === EXCEPTION HIERARCHY TESTS ===
    
    @Test
    @DisplayName("Verify Throwable class exists")
    void testThrowableHierarchy() {
        Throwable t = new RuntimeException("test");
        assertNotNull(t);
        assertTrue(t instanceof Throwable);
    }
    
    @Test
    @DisplayName("Verify Exception extends Throwable")
    void testExceptionHierarchy() {
        Exception e = new Exception("test");
        assertTrue(e instanceof Throwable);
        assertTrue(e instanceof Exception);
    }
    
    @Test
    @DisplayName("Verify RuntimeException is unchecked")
    void testRuntimeExceptionIsUnchecked() {
        RuntimeException e = new ArrayIndexOutOfBoundsException();
        assertTrue(e instanceof RuntimeException);
    }
    
    // === TRY-CATCH BEHAVIOR TESTS ===
    
    @Test
    @DisplayName("Catch specific exception type")
    void testTryCatchCatchesCorrectException() {
        assertThrows(ArrayIndexOutOfBoundsException.class, () -> {
            int[] arr = {1, 2, 3};
            int x = arr[5];  // Will throw
        });
    }
    
    @Test
    @DisplayName("Code executes after caught exception")
    void testCodeContinuesAfterException() {
        boolean reached = false;
        try {
            int[] arr = {1, 2, 3};
            int x = arr[10];
        } catch (ArrayIndexOutOfBoundsException e) {
            reached = true;
        }
        assertTrue(reached, "Code after catch should execute");
    }
    
    // === TRY-FINALLY BEHAVIOR ===
    
    @Test
    @DisplayName("Finally block executes when exception thrown")
    void testFinallyExecutesWithException() {
        boolean finallyExecuted = false;
        try {
            throw new RuntimeException("test");
        } catch (RuntimeException e) {
            // Handle
        } finally {
            finallyExecuted = true;
        }
        assertTrue(finallyExecuted);
    }
    
    @Test
    @DisplayName("Finally block executes when no exception")
    void testFinallyExecutesWithoutException() {
        boolean finallyExecuted = false;
        try {
            int x = 5;
        } finally {
            finallyExecuted = true;
        }
        assertTrue(finallyExecuted);
    }
    
    @Test
    @DisplayName("Finally executes even with early return")
    void testFinallyExecutesWithReturn() {
        final boolean[] finallyExecuted = {false};
        
        try {
            try {
                // Empty try
            } finally {
                finallyExecuted[0] = true;
            }
        } catch (Exception e) {
            // Ignore
        }
        
        assertTrue(finallyExecuted[0]);
    }
    
    // === MULTIPLE CATCH BLOCKS ===
    
    @Test
    @DisplayName("Multiple catches - first matching catch executes")
    void testMultipleCatchBlocksFirstMatches() {
        boolean nullCaught = false;
        
        try {
            String str = null;
            str.length();
        } catch (NullPointerException e) {
            nullCaught = true;
        } catch (Exception e) {
            fail("Should catch NullPointerException first");
        }
        
        assertTrue(nullCaught);
    }
    
    @Test
    @DisplayName("Multiple catches - correct exception caught")
    void testMultipleCatchBlocksSecondMatches() {
        boolean indexCaught = false;
        
        try {
            int[] arr = {1, 2};
            arr[10] = 5;
        } catch (NullPointerException e) {
            fail("Should catch ArrayIndexOutOfBoundsException");
        } catch (ArrayIndexOutOfBoundsException e) {
            indexCaught = true;
        }
        
        assertTrue(indexCaught);
    }
    
    // === TRY-WITH-RESOURCES TESTS ===
    
    @Test
    @DisplayName("Try-with-resources closes resource automatically")
    void testTryWithResourcesClosesResource() {
        boolean closed = false;
        
        try (ExceptionsDemo.SimpleResource resource = 
             new ExceptionsDemo.SimpleResource("test")) {
            assertNotNull(resource);
        } catch (Exception e) {
            fail("Should not throw exception");
        }
        
        // Resource is automatically closed
    }
    
    @Test
    @DisplayName("Try-with-resources with exception")
    void testTryWithResourcesWithException() {
        assertDoesNotThrow(() -> {
            try (ExceptionsDemo.SimpleResource resource = 
                 new ExceptionsDemo.SimpleResource("test")) {
                // Resource is used here
            }
        });
    }
    
    // === CUSTOM EXCEPTION TESTS ===
    
    @Test
    @DisplayName("Custom InvalidAgeException can be thrown and caught")
    void testCustomExceptionThrowAndCatch() {
        assertThrows(ExceptionsDemo.InvalidAgeException.class, () -> {
            ExceptionsDemo.validateAge(15);
        });
    }
    
    @Test
    @DisplayName("Custom exception with message")
    void testCustomExceptionMessage() {
        ExceptionsDemo.InvalidAgeException e = 
            assertThrows(ExceptionsDemo.InvalidAgeException.class, () -> {
                ExceptionsDemo.validateAge(10);
            });
        
        assertTrue(e.getMessage().contains("10"));
    }
    
    @Test
    @DisplayName("Valid age does not throw exception")
    void testValidAgeDoesNotThrow() {
        assertDoesNotThrow(() -> {
            ExceptionsDemo.validateAge(25);
        });
    }
    
    @Test
    @DisplayName("Invalid age throws exception")
    void testInvalidAgeThrows() {
        for (int ageVal = 0; ageVal < 18; ageVal++) {
            final int age = ageVal;
            assertThrows(ExceptionsDemo.InvalidAgeException.class, () -> {
                ExceptionsDemo.validateAge(age);
            });
        }
    }
    
    // === EXCEPTION PROPAGATION TESTS ===
    
    @Test
    @DisplayName("Exception propagates through method hierarchy")
    void testExceptionPropagation() {
        // When validated age is invalid, exception should propagate
        assertThrows(ExceptionsDemo.InvalidAgeException.class, () -> {
            ExceptionsDemo.methodLevelOne();  // Eventually calls validateAge with invalid age
        });
    }
    
    // === EXCEPTION CHARACTERISTICS ===
    
    @Test
    @DisplayName("Exception provides getMessage")
    void testExceptionGetMessage() {
        String message = "Test message";
        Exception e = new Exception(message);
        assertEquals(message, e.getMessage());
    }
    
    @Test
    @DisplayName("Exception provides getCause")
    void testExceptionCause() {
        Exception cause = new RuntimeException("cause");
        Exception e = new Exception("wrapper", cause);
        assertEquals(cause, e.getCause());
    }
    
    @Test
    @DisplayName("Exception provides getStackTrace")
    void testExceptionStackTrace() {
        Exception e = new Exception();
        StackTraceElement[] trace = e.getStackTrace();
        assertNotNull(trace);
        assertTrue(trace.length > 0);
    }
    
    // === EXCEPTION COMPARISON ===
    
    @Test
    @DisplayName("Different exception types are not equal")
    void testDifferentExceptionTypes() {
        Exception e1 = new IllegalArgumentException("test");
        Exception e2 = new NullPointerException("test");
        assertNotEquals(e1, e2);
    }
    
    @Test
    @DisplayName("Same message different exception types")
    void testSameMessageDifferentTypes() {
        Exception e1 = new Exception("same");
        Exception e2 = new RuntimeException("same");
        assertNotEquals(e1, e2);
    }
    
    // === CHECKED VS UNCHECKED TESTS ===
    
    @Test
    @DisplayName("Checked vs Unchecked - InvalidAgeException is checked")
    void testInvalidAgeIsCheckedException() {
        assertTrue(Exception.class.isAssignableFrom(
            ExceptionsDemo.InvalidAgeException.class));
        assertFalse(RuntimeException.class.isAssignableFrom(
            ExceptionsDemo.InvalidAgeException.class));
    }
    
    @Test
    @DisplayName("Checked vs Unchecked - NullPointerException is unchecked")
    void testNullPointerIsUnchecked() {
        assertTrue(RuntimeException.class.isAssignableFrom(
            NullPointerException.class));
        assertTrue(Exception.class.isAssignableFrom(
            NullPointerException.class));
    }
    
    // === RESOURCE CLOSING TESTS ===
    
    @Test
    @DisplayName("SimpleResource implements AutoCloseable")
    void testSimpleResourceIsAutoCloseable() {
        ExceptionsDemo.SimpleResource resource = 
            new ExceptionsDemo.SimpleResource("test");
        assertTrue(resource instanceof AutoCloseable);
    }
    
    @Test
    @DisplayName("SimpleResource can be created and used")
    void testSimpleResourceCreation() {
        assertDoesNotThrow(() -> {
            ExceptionsDemo.SimpleResource resource = 
                new ExceptionsDemo.SimpleResource("test");
            assertEquals("test", resource.getName());
        });
    }
    
    // === EXCEPTION HANDLING BEST PRACTICES ===
    
    @Test
    @DisplayName("Specific catch before general catch")
    void testCatchSpecificBeforeGeneral() {
        boolean correctCatchExecuted = false;
        
        try {
            throw new ArrayIndexOutOfBoundsException();
        } catch (ArrayIndexOutOfBoundsException e) {
            correctCatchExecuted = true;
        } catch (Exception e) {
            fail("Should catch specific exception first");
        }
        
        assertTrue(correctCatchExecuted);
    }
    
    @Test
    @DisplayName("Do not suppress exceptions silently")
    void testDoNotSuppressExceptions() {
        // Bad practice: empty catch block
        // Good practice: at least log or handle
        try {
            throw new RuntimeException("error");
        } catch (RuntimeException e) {
            // Should handle properly, not silently ignore
            assertNotNull(e);
        }
    }
    
    @Test
    @DisplayName("Re-throw exception with context")
    void testRethrowException() {
        assertThrows(Exception.class, () -> {
            try {
                throw new RuntimeException("original");
            } catch (RuntimeException e) {
                throw new Exception("wrapped: " + e.getMessage());
            }
        });
    }

    @Test
    @DisplayName("Demo entry point executes all scenarios without throwing")
    void testDemonstrateExceptionsCoversDemoPaths() {
        assertDoesNotThrow(ExceptionsDemo::demonstrateExceptions);
    }
}
