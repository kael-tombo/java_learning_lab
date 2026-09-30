package com.learning.lambda;

/**
 * Custom functional interface (SAM): single abstract method.
 *
 * Used by Lab.java demos and LambdaTests to demonstrate
 * lambda expressions targeting custom functional interfaces.
 */
@FunctionalInterface
public interface MathOperation {
    int operate(int a, int b);
}
