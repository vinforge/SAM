
  You can now view your Streamlit app in your browser.

  URL: http://localhost:8502

2025-07-08 14:21:42,729 - faiss.loader - INFO - Loading faiss with AVX512 support.
2025-07-08 14:21:42,730 - faiss.loader - INFO - Could not load library with AVX512 support due to:
ModuleNotFoundError("No module named 'faiss.swigfaiss_avx512'")
2025-07-08 14:21:42,730 - faiss.loader - INFO - Loading faiss with AVX2 support.
2025-07-08 14:21:42,749 - faiss.loader - INFO - Successfully loaded faiss with AVX2 support.
2025-07-08 14:21:42,753 - faiss - INFO - Failed to load GPU Faiss: name 'GpuIndexIVFFlat' is not defined. Will not load constructor refs for GPU indexes. This is only an error if you're trying to use GPU Faiss.
2025-07-08 14:21:45,963 - numexpr.utils - INFO - Note: NumExpr detected 32 cores but "NUMEXPR_MAX_THREADS" not set, so enforcing safe limit of 8.
2025-07-08 14:21:45,965 - numexpr.utils - INFO - NumExpr defaulting to 8 threads.
2025-07-08 14:21:47,189 - root - WARNING - Dimension-aware retrieval not available
2025-07-08 14:21:48.770 Examining the path of torch.classes raised: Tried to instantiate class '__path__._path', but it does not exist! Ensure that it is registered via torch::class_
2025-07-08 14:22:04,473 - security.crypto_utils.CryptoManager - INFO - CryptoManager initialized
2025-07-08 14:22:04,473 - security.keystore_manager.KeystoreManager - INFO - KeystoreManager initialized with path: security\keystore.json
2025-07-08 14:22:04,543 - security.crypto_utils.CryptoManager - INFO - Session key set and AES-GCM initialized
2025-07-08 14:22:04,545 - security.keystore_manager.KeystoreManager - INFO - Keystore created successfully: sam_dfb3d56909674fe5
2025-07-08 14:22:04,546 - security.crypto_utils.CryptoManager - INFO - Session key cleared from memory
2025-07-08 14:22:04,546 - security.crypto_utils.CryptoManager - INFO - CryptoManager initialized
2025-07-08 14:22:04,607 - security.crypto_utils.CryptoManager - INFO - Session key set and AES-GCM initialized
2025-07-08 14:22:04.999 Examining the path of torch.classes raised: Tried to instantiate class '__path__._path', but it does not exist! Ensure that it is registered via torch::class_
2025-07-08 14:22:54,491 - security.crypto_utils.CryptoManager - INFO - CryptoManager initialized
2025-07-08 14:22:54,491 - security.keystore_manager.KeystoreManager - INFO - KeystoreManager initialized with path: security\keystore.json
2025-07-08 14:22:54,491 - __main__ - INFO - Security manager initialized
2025-07-08 14:22:54,491 - security.security_ui.SecurityUI - INFO - SecurityUI initialized with real authentication
2025-07-08 14:23:01,710 - security.security_ui.SecurityUI - INFO - SecurityUI initialized with real authentication
2025-07-08 14:23:01,779 - security.crypto_utils.CryptoManager - INFO - Session key set and AES-GCM initialized
2025-07-08 14:23:01,780 - security.keystore_manager.KeystoreManager - INFO - Password verified successfully
2025-07-08 14:23:01,781 - security.crypto_utils.CryptoManager - INFO - CryptoManager initialized
2025-07-08 14:23:01,931 - security.security_ui.SecurityUI - INFO - SecurityUI initialized with real authentication
2025-07-08 14:23:02,439 - sam.entitlements.validator - INFO - EntitlementValidator initialized
2025-07-08 14:23:02,439 - sam.entitlements.feature_manager - INFO - FeatureManager initialized
2025-07-08 14:23:02,472 - memory.ranking_engine - WARNING - Config file not found: config\sam_config.json, using defaults
2025-07-08 14:23:02,473 - memory.ranking_engine - INFO - Memory Ranking Engine initialized
2025-07-08 14:23:02,473 - memory.ranking_engine - INFO -   Weights: semantic=0.60, recency=0.15, confidence=0.20, priority=0.05
2025-07-08 14:23:02,473 - memory.ranking_engine - INFO -   Config: candidates=50, decay_days=30.0
2025-07-08 14:23:02,473 - memory.memory_vectorstore - INFO - Memory Ranking Engine initialized for hybrid search
2025-07-08 14:23:02,724 - chromadb.telemetry.product.posthog - ERROR - Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
2025-07-08 14:23:02,739 - chromadb.telemetry.product.posthog - ERROR - Failed to send telemetry event ClientCreateCollectionEvent: capture() takes 1 positional argument but 3 were given
2025-07-08 14:23:02,739 - memory.memory_vectorstore - INFO - Initialized enhanced Chroma vector store: sam_memory_store
2025-07-08 14:23:02,741 - memory.memory_vectorstore - INFO - Collection count: 0
2025-07-08 14:23:02,741 - chromadb.telemetry.product.posthog - ERROR - Failed to send telemetry event CollectionGetEvent: capture() takes 1 positional argument but 3 were given
2025-07-08 14:23:02,742 - memory.memory_vectorstore - INFO - No existing memories found in ChromaDB
2025-07-08 14:23:02,742 - memory.memory_vectorstore - INFO - Memory vector store initialized: chroma with 0 memories
2025-07-08 14:23:02,742 - memory.memory_manager - INFO - Long-term memory manager initialized with 0 memories
2025-07-08 14:23:02,742 - memory.secure_memory_vectorstore - INFO - SecureMemoryVectorStore initialized with chroma backend
2025-07-08 14:23:02,743 - memory.secure_memory_vectorstore - INFO - Security integration enabled
2025-07-08 14:23:02,743 - __main__ - INFO - Secure memory store initialized with security integration
2025-07-08 14:23:02,743 - memory.secure_memory_vectorstore - INFO - ✅ Encryption activated for secure memory store
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 68: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 276, in initialize_secure_sam
    if st.session_state.secure_memory_store.activate_encryption():
  File "G:\SAM\memory\secure_memory_vectorstore.py", line 312, in activate_encryption
    logger.info("✅ Encryption activated for secure memory store")
Message: '✅ Encryption activated for secure memory store'
Arguments: ()
2025-07-08 14:23:02,746 - __main__ - INFO - ✅ Encryption activated for secure memory store
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 277, in initialize_secure_sam
    logger.info("✅ Encryption activated for secure memory store")
Message: '✅ Encryption activated for secure memory store'
Arguments: ()
2025-07-08 14:23:02,747 - utils.embedding_utils - INFO - Loading embedding model: all-MiniLM-L6-v2
2025-07-08 14:23:02,747 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: all-MiniLM-L6-v2
modules.json: 100%|████████████████████████████████████████████████████████████████████████| 349/349 [00:00<?, ?B/s]
C:\Users\vin\anaconda3\Lib\site-packages\huggingface_hub\file_download.py:144: UserWarning: `huggingface_hub` cache-system uses symlinks by default to efficiently store duplicated files but your machine does not support them in G:\SAM\models\embeddings\models--sentence-transformers--all-MiniLM-L6-v2. Caching files will still work but in a degraded version that might require more space on your disk. This warning can be disabled by setting the `HF_HUB_DISABLE_SYMLINKS_WARNING` environment variable. For more details, see https://huggingface.co/docs/huggingface_hub/how-to-cache#limitations.
To support symlinks on Windows, you either need to activate Developer Mode or to run Python as an administrator. In order to activate developer mode, see this article: https://docs.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development
  warnings.warn(message)
config_sentence_transformers.json: 100%|████████████████████████████████████████████| 116/116 [00:00<00:00, 116kB/s]
README.md: 10.5kB [00:00, ?B/s]
sentence_bert_config.json: 100%|█████████████████████████████████████████████████████████| 53.0/53.0 [00:00<?, ?B/s]
config.json: 100%|█████████████████████████████████████████████████████████████████████████| 612/612 [00:00<?, ?B/s]
Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
2025-07-08 14:23:05,743 - huggingface_hub.file_download - WARNING - Xet Storage is enabled for this repo, but the 'hf_xet' package is not installed. Falling back to regular HTTP download. For better performance, install the package with: `pip install huggingface_hub[hf_xet]` or `pip install hf_xet`
model.safetensors: 100%|███████████████████████████████████████████████████████| 90.9M/90.9M [00:01<00:00, 60.3MB/s]
tokenizer_config.json: 100%|████████████████████████████████████████████████████████| 350/350 [00:00<00:00, 349kB/s]
vocab.txt: 232kB [00:00, 13.6MB/s]
tokenizer.json: 466kB [00:00, 32.1MB/s]
special_tokens_map.json: 100%|█████████████████████████████████████████████████████████████| 112/112 [00:00<?, ?B/s]
2025-07-08 14:23:07,727 - security.security_ui.SecurityUI - INFO - SecurityUI initialized with real authentication
2025-07-08 14:23:07,795 - memory.secure_memory_vectorstore - INFO - ✅ Encryption activated for secure memory store
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 68: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 286, in initialize_secure_sam
    encryption_activated = st.session_state.secure_memory_store.activate_encryption()
  File "G:\SAM\memory\secure_memory_vectorstore.py", line 312, in activate_encryption
    logger.info("✅ Encryption activated for secure memory store")
Message: '✅ Encryption activated for secure memory store'
Arguments: ()
2025-07-08 14:23:07,798 - __main__ - INFO - ✅ Encryption activated for existing memory store
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 288, in initialize_secure_sam
    logger.info("✅ Encryption activated for existing memory store")
Message: '✅ Encryption activated for existing memory store'
Arguments: ()
2025-07-08 14:23:07,800 - utils.embedding_utils - INFO - Loading embedding model: all-MiniLM-L6-v2
2025-07-08 14:23:07,800 - sentence_transformers.SentenceTransformer - INFO - Load pretrained SentenceTransformer: all-MiniLM-L6-v2
config.json: 100%|█████████████████████████████████████████████████████████████████████████| 190/190 [00:00<?, ?B/s]
2025-07-08 14:23:07,918 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: cuda
Batches:   0%|                                                                                | 0/1 [00:00<?, ?it/s]2025-07-08 14:23:08,297 - sentence_transformers.SentenceTransformer - INFO - Use pytorch device_name: cuda
Batches: 100%|████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  9.06it/s]
Batches: 100%|████████████████████████████████████████████████████████████████████████| 1/1 [00:00<00:00,  2.57it/s]2025-07-08 14:23:08,452 - utils.embedding_utils - INFO - Model loaded successfully, embedding dim: 384

2025-07-08 14:23:08,452 - utils.embedding_utils - INFO - Model loaded successfully, embedding dim: 384
2025-07-08 14:23:08,452 - utils.embedding_utils - INFO - Embedding manager initialized with model: all-MiniLM-L6-v2
2025-07-08 14:23:08,453 - utils.embedding_utils - INFO - Embedding manager initialized with model: all-MiniLM-L6-v2
2025-07-08 14:23:08,453 - utils.embedding_utils - INFO - Embedding dimension: 384
2025-07-08 14:23:08,453 - utils.embedding_utils - INFO - Embedding dimension: 384
2025-07-08 14:23:08,453 - __main__ - INFO - ✅ Embedding manager initialized
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 295, in initialize_secure_sam
    logger.info("✅ Embedding manager initialized")
Message: '✅ Embedding manager initialized'
Arguments: ()
2025-07-08 14:23:08,650 - utils.vector_manager - INFO - No existing FAISS index found, starting fresh
2025-07-08 14:23:08,650 - utils.vector_manager - INFO - Vector manager initialized with 0 vectors using FAISS backend
2025-07-08 14:23:08,650 - __main__ - INFO - ✅ Vector manager initialized
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 304, in initialize_secure_sam
    logger.info("✅ Vector manager initialized")
Message: '✅ Vector manager initialized'
Arguments: ()
2025-07-08 14:23:08,701 - multimodal_processing.document_parser - INFO - Multimodal document parser initialized
2025-07-08 14:23:08,701 - multimodal_processing.document_parser - INFO - Supported formats: .docx, .cpp, .pdf, .md, .js, .java, .c, .html, .htm, .txt, .py
2025-07-08 14:23:08,701 - multimodal_processing.knowledge_consolidator - INFO - Knowledge consolidator initialized
2025-07-08 14:23:08,701 - multimodal_processing.enrichment_scorer - INFO - Multimodal enrichment scorer initialized
2025-07-08 14:23:08,701 - multimodal_processing.enrichment_scorer - INFO - Scoring weights: {'content_diversity': 0.25, 'technical_depth': 0.2, 'information_density': 0.2, 'structural_quality': 0.15, 'multimodal_integration': 0.1, 'novelty_potential': 0.1}
2025-07-08 14:23:08,702 - utils.vector_manager - INFO - No existing FAISS index found, starting fresh
2025-07-08 14:23:08,702 - utils.vector_manager - INFO - Vector manager initialized with 0 vectors using FAISS backend
2025-07-08 14:23:08,702 - memory.ranking_engine - WARNING - Config file not found: config\sam_config.json, using defaults
2025-07-08 14:23:08,702 - memory.ranking_engine - INFO - Memory Ranking Engine initialized
2025-07-08 14:23:08,702 - memory.ranking_engine - INFO -   Weights: semantic=0.60, recency=0.15, confidence=0.20, priority=0.05
2025-07-08 14:23:08,702 - memory.ranking_engine - INFO -   Config: candidates=50, decay_days=30.0
2025-07-08 14:23:08,702 - memory.memory_vectorstore - INFO - Memory Ranking Engine initialized for hybrid search
2025-07-08 14:23:08,702 - memory.memory_vectorstore - INFO - Initialized simple vector store
2025-07-08 14:23:08,703 - memory.memory_vectorstore - INFO - Loaded 0 existing memories
2025-07-08 14:23:08,703 - memory.memory_vectorstore - INFO - Memory vector store initialized: simple with 0 memories
2025-07-08 14:23:08,703 - sam.cognition.table_processing.table_parser - INFO - TableParser initialized with 5 strategies
2025-07-08 14:23:08,703 - sam.cognition.table_processing.role_classifier - INFO - No trained model found, using enhanced heuristic-based classification
2025-07-08 14:23:08,703 - sam.cognition.table_processing.role_classifier - INFO - TableRoleClassifier initialized
2025-07-08 14:23:08,703 - sam.cognition.table_processing.table_validator - INFO - TableValidator initialized
2025-07-08 14:23:08,703 - sam.cognition.table_processing.table_enhancer - INFO - TableEnhancer initialized
2025-07-08 14:23:08,703 - sam.cognition.table_processing.sam_integration - INFO - TableAwareChunker initialized
2025-07-08 14:23:08,704 - multimodal_processing.multimodal_pipeline - INFO - Multimodal processing pipeline initialized
2025-07-08 14:23:08,704 - multimodal_processing.multimodal_pipeline - INFO - Output directory: multimodal_output
2025-07-08 14:23:08,704 - __main__ - INFO - ✅ Multimodal pipeline initialized
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 313, in initialize_secure_sam
    logger.info("✅ Multimodal pipeline initialized")
Message: '✅ Multimodal pipeline initialized'
Arguments: ()
2025-07-08 14:23:08,777 - reasoning.self_decide_framework - INFO - SELF-DECIDE framework initialized
2025-07-08 14:23:08,777 - __main__ - INFO - ✅ Tool-augmented reasoning initialized
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 322, in initialize_secure_sam
    logger.info("✅ Tool-augmented reasoning initialized")
Message: '✅ Tool-augmented reasoning initialized'
Arguments: ()
2025-07-08 14:23:08,911 - integrate_slp_enhancements - INFO - 🧠 Initializing Enhanced SLP System...
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\U0001f9e0' in position 62: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 330, in initialize_secure_sam
    slp_integration = integrate_enhanced_slp_into_sam()
  File "G:\SAM\integrate_slp_enhancements.py", line 784, in integrate_enhanced_slp_into_sam
    slp_integration = initialize_enhanced_slp_system()
  File "G:\SAM\integrate_slp_enhancements.py", line 37, in initialize_enhanced_slp_system
    logger.info("🧠 Initializing Enhanced SLP System...")
Message: '🧠 Initializing Enhanced SLP System...'
Arguments: ()
2025-07-08 14:23:08,943 - sam.cognition.slp.latent_program_store - INFO - Latent program database with enhanced analytics initialized successfully
2025-07-08 14:23:08,944 - sam.cognition.slp.analytics_engine - INFO - SLP Analytics Engine initialized
2025-07-08 14:23:08,945 - sam.cognition.slp.latent_program_store - INFO - Latent program database with enhanced analytics initialized successfully
2025-07-08 14:23:08,945 - sam.cognition.slp.metrics_collector - INFO - SLP Metrics Collector initialized with 60s interval
2025-07-08 14:23:08,945 - sam.cognition.slp.latent_program_store - INFO - Latent program database with enhanced analytics initialized successfully
2025-07-08 14:23:08,946 - sam.cognition.slp.program_validator - INFO - Program validator initialized
2025-07-08 14:23:08,946 - sam.cognition.slp.metrics_collector - INFO - Started SLP metrics collection
2025-07-08 14:23:08,947 - sam.cognition.slp.program_manager - INFO - Program manager initialized with enhanced analytics support
2025-07-08 14:23:08,947 - sam.cognition.slp.sam_slp_integration - INFO - SAM-SLP integration initialized with enhanced analytics
2025-07-08 14:23:08,947 - integrate_slp_enhancements - INFO - ✅ Enhanced analytics engine detected
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 62: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 330, in initialize_secure_sam
    slp_integration = integrate_enhanced_slp_into_sam()
  File "G:\SAM\integrate_slp_enhancements.py", line 784, in integrate_enhanced_slp_into_sam
    slp_integration = initialize_enhanced_slp_system()
  File "G:\SAM\integrate_slp_enhancements.py", line 57, in initialize_enhanced_slp_system
    logger.info("✅ Enhanced analytics engine detected")
Message: '✅ Enhanced analytics engine detected'
Arguments: ()
2025-07-08 14:23:08,948 - sam.cognition.slp.program_analyzer - INFO - Program Analyzer initialized
2025-07-08 14:23:08,948 - sam.cognition.slp.cognitive_insights - INFO - Cognitive Insights Generator initialized
2025-07-08 14:23:08,948 - integrate_slp_enhancements - INFO - ✅ Advanced analysis components initialized
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 62: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 330, in initialize_secure_sam
    slp_integration = integrate_enhanced_slp_into_sam()
  File "G:\SAM\integrate_slp_enhancements.py", line 784, in integrate_enhanced_slp_into_sam
    slp_integration = initialize_enhanced_slp_system()
  File "G:\SAM\integrate_slp_enhancements.py", line 71, in initialize_enhanced_slp_system
    logger.info("✅ Advanced analysis components initialized")
Message: '✅ Advanced analysis components initialized'
Arguments: ()
2025-07-08 14:23:08,949 - integrate_slp_enhancements - INFO - ✅ Enhanced SLP system initialized successfully
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 62: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 330, in initialize_secure_sam
    slp_integration = integrate_enhanced_slp_into_sam()
  File "G:\SAM\integrate_slp_enhancements.py", line 784, in integrate_enhanced_slp_into_sam
    slp_integration = initialize_enhanced_slp_system()
  File "G:\SAM\integrate_slp_enhancements.py", line 73, in initialize_enhanced_slp_system
    logger.info("✅ Enhanced SLP system initialized successfully")
Message: '✅ Enhanced SLP system initialized successfully'
Arguments: ()
2025-07-08 14:23:08,950 - integrate_slp_enhancements - INFO - ✅ Enhanced SLP integration successful
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 62: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 330, in initialize_secure_sam
    slp_integration = integrate_enhanced_slp_into_sam()
  File "G:\SAM\integrate_slp_enhancements.py", line 787, in integrate_enhanced_slp_into_sam
    logger.info("✅ Enhanced SLP integration successful")
Message: '✅ Enhanced SLP integration successful'
Arguments: ()
2025-07-08 14:23:08,951 - __main__ - INFO - ✅ Enhanced SLP system (Phase 1A+1B) initialized
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 335, in initialize_secure_sam
    logger.info("✅ Enhanced SLP system (Phase 1A+1B) initialized")
Message: '✅ Enhanced SLP system (Phase 1A+1B) initialized'
Arguments: ()
2025-07-08 14:23:09,040 - sam.cognition.dissonance_monitor - INFO - DissonanceMonitor initialized: vocab_size=32000, mode=entropy, device=cuda
2025-07-08 14:23:09,040 - sam.cognition.tpv.tpv_monitor - INFO - Dissonance monitor initialized successfully
2025-07-08 14:23:09,040 - sam.cognition.tpv.tpv_monitor - INFO - TPVMonitor initialized (dissonance_monitoring=True)
2025-07-08 14:23:09,040 - sam.cognition.tpv.tpv_controller - INFO - ReasoningController initialized: mode=passive, dissonance_control=True
2025-07-08 14:23:09,040 - sam.cognition.tpv.tpv_trigger - INFO - TPVTrigger initialized
2025-07-08 14:23:09,051 - sam.cognition.tpv.tpv_config - INFO - Loaded TPV config from G:\SAM\sam\cognition\tpv\tpv_config.yaml
2025-07-08 14:23:09,051 - sam.cognition.tpv.sam_integration - INFO - SAM-TPV Integration initialized
2025-07-08 14:23:09,051 - sam.cognition.tpv.sam_integration - INFO - TPV enabled by default: False
2025-07-08 14:23:09,051 - sam.cognition.tpv.tpv_monitor - INFO - TPV Monitor initialization completed
2025-07-08 14:23:09,051 - sam.cognition.tpv.sam_integration - INFO - ✅ SAM-TPV Integration initialization completed
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 69: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 350, in initialize_secure_sam
    tpv_init_success = sam_tpv_integration.initialize()
  File "G:\SAM\sam\cognition\tpv\sam_integration.py", line 81, in initialize
    logger.info("✅ SAM-TPV Integration initialization completed")
Message: '✅ SAM-TPV Integration initialization completed'
Arguments: ()
2025-07-08 14:23:09,052 - __main__ - INFO - ✅ TPV system initialized and ready for Active Reasoning Control
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 355, in initialize_secure_sam
    logger.info("✅ TPV system initialized and ready for Active Reasoning Control")
Message: '✅ TPV system initialized and ready for Active Reasoning Control'
Arguments: ()
2025-07-08 14:23:09,053 - __main__ - WARNING - MEMOIR integration not available: No module named 'sam.orchestration.memoir_sof_integration'
2025-07-08 14:23:09,111 - sam.discovery.distillation.schema - INFO - Cognitive distillation tables created successfully
2025-07-08 14:23:09,111 - sam.discovery.distillation.schema - INFO - Distillation database schema initialized
2025-07-08 14:23:09,111 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,121 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,130 - sam.discovery.distillation.validator - INFO - Enhanced principle validator initialized for Phase 1B
2025-07-08 14:23:09,137 - sam.discovery.distillation.llm_integration - INFO - LLM integration initialized
2025-07-08 14:23:09,137 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,137 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,137 - sam.discovery.distillation.validator - INFO - Enhanced principle validator initialized for Phase 1B
2025-07-08 14:23:09,137 - sam.discovery.distillation.llm_integration - INFO - LLM integration initialized
2025-07-08 14:23:09,137 - sam.discovery.distillation.engine - INFO - Distillation engine initialized with LLM integration
2025-07-08 14:23:09,146 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,147 - sam.discovery.distillation.prompt_augmentation - INFO - Prompt augmentation system initialized
2025-07-08 14:23:09,154 - sam.discovery.distillation.thought_transparency - INFO - Thought transparency system initialized
2025-07-08 14:23:09,162 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,162 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,162 - sam.discovery.distillation.validator - INFO - Enhanced principle validator initialized for Phase 1B
2025-07-08 14:23:09,162 - sam.discovery.distillation.llm_integration - INFO - LLM integration initialized
2025-07-08 14:23:09,162 - sam.discovery.distillation.engine - INFO - Distillation engine initialized with LLM integration
2025-07-08 14:23:09,162 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,162 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,163 - sam.discovery.distillation.automation - INFO - Automated distillation system initialized
2025-07-08 14:23:09,170 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,170 - sam.discovery.distillation.prompt_augmentation - INFO - Prompt augmentation system initialized
2025-07-08 14:23:09,170 - sam.discovery.distillation.thought_transparency - INFO - Thought transparency system initialized
2025-07-08 14:23:09,170 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,170 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,170 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,171 - sam.discovery.distillation.validator - INFO - Enhanced principle validator initialized for Phase 1B
2025-07-08 14:23:09,171 - sam.discovery.distillation.llm_integration - INFO - LLM integration initialized
2025-07-08 14:23:09,171 - sam.discovery.distillation.engine - INFO - Distillation engine initialized with LLM integration
2025-07-08 14:23:09,171 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,171 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,171 - sam.discovery.distillation.automation - INFO - Automated distillation system initialized
2025-07-08 14:23:09,171 - sam.discovery.distillation.automation - INFO - Added trigger 00a375f4-3abc-4706-bfd4-ebc217000392 for strategy financial_analysis
2025-07-08 14:23:09,171 - sam.discovery.distillation.automation - INFO - Added trigger 01a086b6-7920-4e50-9a1b-334a7a5d20b0 for strategy technical_support
2025-07-08 14:23:09,171 - sam.discovery.distillation.automation - INFO - Added trigger 36ab64b4-e17a-4dba-a62d-0f33b55b2f7a for strategy research_queries
2025-07-08 14:23:09,171 - sam.discovery.distillation.automation - INFO - Setup 3 default triggers
2025-07-08 14:23:09,172 - sam.discovery.distillation.automation - INFO - Automation loop started
2025-07-08 14:23:09,172 - sam.discovery.distillation.automation - INFO - Automated distillation started
2025-07-08 14:23:09,173 - sam.discovery.distillation.sam_integration - INFO - SAM cognitive distillation integration initialized
2025-07-08 14:23:09,175 - sam.discovery.distillation.automation - INFO - Trigger activated: 36ab64b4-e17a-4dba-a62d-0f33b55b2f7a
2025-07-08 14:23:09,175 - sam.discovery.distillation.automation - INFO - Running automated distillation for strategy: research_queries
2025-07-08 14:23:09,177 - sam.discovery.distillation.engine - INFO - Collecting interactions for strategy research_queries
2025-07-08 14:23:09,190 - sam.discovery.distillation.optimization - INFO - Semantic cache initialized
2025-07-08 14:23:09,190 - sam.discovery.distillation.optimization - INFO - Principle optimizer initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.optimization - INFO - Performance monitor initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.prompt_augmentation - INFO - Prompt augmentation system initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.thought_transparency - INFO - Thought transparency system initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.validator - INFO - Enhanced principle validator initialized for Phase 1B
2025-07-08 14:23:09,191 - sam.discovery.distillation.llm_integration - INFO - LLM integration initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.engine - INFO - Distillation engine initialized with LLM integration
2025-07-08 14:23:09,191 - sam.discovery.distillation.registry - INFO - Principle registry initialized
2025-07-08 14:23:09,191 - sam.discovery.distillation.collector - INFO - Interaction collector initialized
2025-07-08 14:23:09,192 - sam.discovery.distillation.automation - INFO - Automated distillation system initialized
2025-07-08 14:23:09,192 - sam.discovery.distillation.automation - INFO - Added trigger e613e705-fa9e-4c99-a7ee-4d9b3cd3f2dd for strategy financial_analysis
2025-07-08 14:23:09,192 - sam.discovery.distillation.automation - INFO - Added trigger c54e1ead-e295-40fc-806c-1656e0c92cd4 for strategy technical_support
2025-07-08 14:23:09,192 - sam.discovery.distillation.automation - INFO - Added trigger 8260e790-63fb-46d8-baf4-451b773e5c3e for strategy research_queries
2025-07-08 14:23:09,192 - sam.discovery.distillation.automation - INFO - Setup 3 default triggers
2025-07-08 14:23:09,193 - sam.discovery.distillation.automation - INFO - Automation loop started
2025-07-08 14:23:09,193 - sam.discovery.distillation.automation - INFO - Automated distillation started
2025-07-08 14:23:09,193 - sam.discovery.distillation.sam_integration - INFO - SAM cognitive distillation integration initialized
2025-07-08 14:23:09,193 - __main__ - INFO - ✅ Cognitive Distillation Engine initialized with automated principle discovery
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
2025-07-08 14:23:09,194 - sam.discovery.distillation.automation - INFO - Trigger activated: 8260e790-63fb-46d8-baf4-451b773e5c3e
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 392, in initialize_secure_sam
    logger.info("✅ Cognitive Distillation Engine initialized with automated principle discovery")
Message: '✅ Cognitive Distillation Engine initialized with automated principle discovery'
Arguments: ()
2025-07-08 14:23:09,194 - sam.discovery.distillation.automation - INFO - Added trigger 85f7d6eb-f729-4c86-b4fc-2752b965104a for strategy secure_chat_reasoning
2025-07-08 14:23:09,194 - sam.discovery.distillation.automation - INFO - Running automated distillation for strategy: research_queries
2025-07-08 14:23:09,194 - sam.discovery.distillation.automation - INFO - Added trigger e69059ea-28e8-4cdd-b1c3-9c9b285876d1 for strategy document_analysis
2025-07-08 14:23:09,194 - sam.discovery.distillation.automation - INFO - Added trigger ea9af886-96b7-4744-9305-cd88f1e9be6d for strategy web_search_integration
2025-07-08 14:23:09,195 - __main__ - INFO - ✅ Cognitive distillation automation triggers configured
--- Logging error ---
Traceback (most recent call last):
  File "C:\Users\vin\anaconda3\Lib\logging\__init__.py", line 1163, in emit
    stream.write(msg + self.terminator)
  File "C:\Users\vin\anaconda3\Lib\encodings\cp1252.py", line 19, in encode
    return codecs.charmap_encode(input,self.errors,encoding_table)[0]
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
UnicodeEncodeError: 'charmap' codec can't encode character '\u2705' in position 44: character maps to <undefined>
Call stack:
2025-07-08 14:23:09,196 - sam.discovery.distillation.engine - INFO - Collecting interactions for strategy research_queries
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1032, in _bootstrap
    self._bootstrap_inner()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1075, in _bootstrap_inner
    self.run()
  File "C:\Users\vin\anaconda3\Lib\threading.py", line 1012, in run
    self._target(*self._args, **self._kwargs)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 313, in _run_script_thread
    self._run_script(request.rerun_data)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 592, in _run_script
    ) = exec_func_with_error_handling(code_to_exec, ctx)
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\exec_code.py", line 85, in exec_func_with_error_handling
    result = func()
  File "C:\Users\vin\anaconda3\Lib\site-packages\streamlit\runtime\scriptrunner\script_runner.py", line 576, in code_to_exec
    exec(code, module.__dict__)
  File "G:\SAM\secure_streamlit_app.py", line 11996, in <module>
    main()
  File "G:\SAM\secure_streamlit_app.py", line 107, in main
    render_main_sam_application()
  File "G:\SAM\secure_streamlit_app.py", line 214, in render_main_sam_application
    initialize_secure_sam()
  File "G:\SAM\secure_streamlit_app.py", line 427, in initialize_secure_sam
    logger.info("✅ Cognitive distillation automation triggers configured")
Message: '✅ Cognitive distillation automation triggers configured'
Arguments: ()
2025-07-08 14:23:09,248 - sam.conversation.contextual_relevance.ContextualRelevanceEngine - INFO - Using SAM MemoryVectorStore for embeddings
2025-07-08 14:23:09,248 - sam.conversation.contextual_relevance.ContextualRelevanceEngine - INFO - ContextualRelevanceEngine initialized
2025-07-08 14:23:09,262 - sam.discovery.distillation.collector - INFO - Collected 0 successful interactions for strategy research_queries
2025-07-08 14:23:09,262 - sam.discovery.distillation.collector - INFO - Collected 0 successful interactions for strategy research_queries
2025-07-08 14:23:09,263 - sam.discovery.distillation.engine - WARNING - Insufficient interactions (0) for principle discovery
2025-07-08 14:23:09,263 - sam.discovery.distillation.engine - WARNING - Insufficient interactions (0) for principle discovery
2025-07-08 14:23:09,265 - sam.discovery.distillation.automation - WARNING - Failed to discover principle for strategy: research_queries
2025-07-08 14:23:09,271 - sam.discovery.distillation.automation - WARNING - Failed to discover principle for strategy: research_queries
2025-07-08 14:23:09,273 - sam.discovery.distillation.automation - INFO - Trigger activated: ea9af886-96b7-4744-9305-cd88f1e9be6d
2025-07-08 14:23:09,273 - sam.discovery.distillation.automation - INFO - Running automated distillation for strategy: web_search_integration
2025-07-08 14:23:09,275 - sam.discovery.distillation.engine - INFO - Collecting interactions for strategy web_search_integration
2025-07-08 14:23:09,278 - sam.discovery.distillation.collector - INFO - Collected 0 successful interactions for strategy web_search_integration
2025-07-08 14:23:09,278 - sam.discovery.distillation.engine - WARNING - Insufficient interactions (0) for principle discovery
2025-07-08 14:23:09,279 - sam.discovery.distillation.automation - WARNING - Failed to discover principle for strategy: web_search_integration
2025-07-08 14:23:09,302 - sam.session.state_manager.SessionManager - INFO - Loaded 2 sessions from disk
2025-07-08 14:23:09,302 - sam.session.state_manager.SessionManager - INFO - SessionManager initialized with buffer depth: 10
2025-07-08 14:23:09,323 - memory.memory_reasoning - INFO - Memory-driven reasoning engine initialized
2025-07-08 14:23:09,323 - ui.role_memory_filter - INFO - Role-based memory filter initialized
2025-07-08 14:23:09.642 Examining the path of torch.classes raised: Tried to instantiate class '__path__._path', but it does not exist! Ensure that it is registered via torch::class_