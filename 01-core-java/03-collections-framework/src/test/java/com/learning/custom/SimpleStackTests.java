package com.learning.custom;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.Arrays;
import java.util.EmptyStackException;
import java.util.List;

import static org.assertj.core.api.Assertions.assertThat;
import static org.junit.jupiter.api.Assertions.assertThrows;

/**
 * Focused tests for SimpleStack bulk operations and edge cases.
 */
@DisplayName("SimpleStack Tests")
class SimpleStackTests {

    @Test
    @DisplayName("Bulk operations delegate correctly")
    void testBulkOperations() {
        CustomCollectionExample.SimpleStack<String> stack = new CustomCollectionExample.SimpleStack<>();
        assertThat(stack.isEmpty()).isTrue();

        stack.addAll(List.of("a", "b", "c"));
        assertThat(stack.size()).isEqualTo(3);
        assertThat(stack.containsAll(List.of("a", "b"))).isTrue();
        assertThat(stack.toArray()).hasSize(3);
        assertThat(stack.toArray(new String[0])).containsExactly("a", "b", "c");

        stack.retainAll(List.of("a", "b"));
        assertThat(stack).containsExactly("a", "b");

        stack.removeAll(List.of("a"));
        assertThat(stack).containsExactly("b");

        stack.clear();
        assertThat(stack.isEmpty()).isTrue();
    }

    @Test
    @DisplayName("Pop and peek on empty stack throw")
    void testEmptyStackThrows() {
        CustomCollectionExample.SimpleStack<String> stack = new CustomCollectionExample.SimpleStack<>();
        assertThrows(EmptyStackException.class, stack::pop);
        assertThrows(EmptyStackException.class, stack::peek);
    }

    @Test
    @DisplayName("Remove delegates correctly")
    void testRemove() {
        CustomCollectionExample.SimpleStack<String> stack = new CustomCollectionExample.SimpleStack<>();
        stack.push("x");
        assertThat(stack.remove("x")).isTrue();
        assertThat(stack.remove("missing")).isFalse();
        assertThat(Arrays.asList(stack.toArray())).isEmpty();
    }
}
