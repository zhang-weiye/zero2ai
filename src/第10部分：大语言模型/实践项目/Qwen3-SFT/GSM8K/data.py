"""
This module contains the following features:
- Download datasets: GSM8K
- Split the dataset train/valid/test
- construct the prompt
- tokenize
- response only label masking
- dynamic padding
- pytorch batch
"""

from __future__ import annotations

from dataclass import dataclass
from functools import partial
from typing import Any, Mapping, Sequence, TypedDict

import torch
from datasets import DatasetDict, load_dataset
from transformers import PreTrainedTokenizerBase


IGNORE_INDEX = -100

INSTRUCTION = (
    'Solve the following math problem step by step. '
    'End your response with "#### <final answer>".'
)
PROMPT_PREFIX = f"### Instruction:\n{INSTRUCTION}\n\n### Input:\n"
RESPONSE_HEADER = "\n\n### Response:\n"


class TokenizedExample(TypedDict):
    input_ids: list[int]
    attention_mask: list[int]
    labels: list[int]
    sequence_length: int
    prompt_length: int
    respose_length: int


class SFTBatch(TypedDict):
    input_ids: torch.Tensor
    attention_mask: torch.Tensor
    labels: torch.Tensor


@dataclass(frozen=True)
class DataConfig:
    dataset_name: str = "openai/gsm8k"
    dataset_config: str = "main"
    validation_size: int = 500
    seed: int = 51
    max_length: int = 512
    num_proc: int | None = None


def configure_tokenizer(tokenizer: PreTrainedTokenizerBase) -> None:
    """Configure a tokenizer for right-padded causal language-model batches.
    
    Args:
        tokenzier: Tokenizer to configure in place.
        
    Raises:
        ValueError: If the tokenizer does not define an EOS token.
    """
    
    if tokenizer.eos_token_id is None:
        raise ValueError("The tokenizer must define an EOS token.")
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"
    
    
def build_prompt(question: str) -> str:
    """Build instruction prompt for the math problem.
    
    use encode_prompt function to produce input_ids,
    and apply the question-only truncation policy.
    
    Args:
        question: GSM8K problem.
        
    Returns:
        Formatted instruction, input, and response header text.
        
    Raises:
        ValueError: if question is empty after stripping whitespace.
    """
    
    question = question.strip()
    if not question:
        raise ValueError("GSM8K question must not be empty.")
    return f"{PROMPT_PREFIX}{question}{RESPONSE_HEADER}"


def _encode_without_special_tokens(
    tokenizer: PreTrainedTokenizerBase,
    text: str,
) -> list[int]:
    """Encode text without letting the tokenizer insert BOS or EOS tokens."""
    token_ids = tokenizer(text, add_special_tokens=False)["input_ids"]
    return list[token_ids]


def encode_prompt(
    question: str,
    tokenizer: PreTrainedTokenizerBase,
    max_prompt_length: int,
) -> list[int]:
    """Encode a prompt while truncating only the question when necessary.
    
    Args:
        question: GSM8K problem.
        tokenizer: Tokenizer used by the target causal language model.
        max_prompt_length: Maximum number of prompt tokens to return.
        
    Returns:
        Prompt Token IDs ending immediately after ``### Response:``.
        
    Raises:
        ValueError: If the token budget cannot fit the fixed prompt text.
    """
    
    prefix_ids = _encode_without_special_tokens(tokenizer, PROMPT_PREFIX)
    question_ids = _encode_without_special_tokens(tokenizer, question.strip())
    header_ids = _encode_without_special_tokens(tokenizer, RESPONSE_HEADER)
    
    fixed_length = len(prefix_ids) + len(header_ids)
    if max_prompt_length < fixed_length:
        raise ValueError(
            "max_prompt length is too small even for the fixed prompt: "
            f"need at least {fixed_length}, got {max_prompt_length}."
        )        
        
    question_budget = max_prompt_length - fixed_length
    question_ids = question_ids[:question_budget]
    return prefix_ids + question_ids + header_ids

    
def tokenize_sft_example(
    example: Mapping[str, Any],
    tokenizer: PreTrainedTokenizerBase,
    max_length: int,
) -> TokenizedExample:
    """Convert one GSM8K row to a response-only causal-LM example."""
    
    question = str(example["question"]).strip()
    answer = str(example["answer"]).strip()
    if not question or not answer:
        raise ValueError("Question and answer must both be non-empty.")
    
    response_ids = _encode_without_special_tokens(tokenizer, answer)
    eos_token_id = tokenizer.eos_token_id
    if eos_token_id is None:
        raise ValueError("The tokenizer must define an EOS token.")
    if not response_ids or response_ids[-1] != eos_token_id:
        response_ids.append(eos_token_id)
        
    prompt_budget = max_length - len(response_ids)
    prompt_ids = encode_prompt(
        question=question,
        tokenizer=tokenizer,
        max_prompt_length=prompt_budget,
    )
    
    input_ids = prompt_ids + response_ids
    labels = [IGNORE_INDEX] * len(prompt_ids) + 
    
    