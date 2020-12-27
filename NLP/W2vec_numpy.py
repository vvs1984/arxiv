import numpy as np 

def generate_dictinoary_data(text):
    """
    генерация словарей
    вход  - текст в виде одной строки
    выход:
    word_to_index - словарь вида Слово - индекс слова, 
    index_to_word - словарь вида индекс слова - Слово, 
    corpus список набора слов, 
    vocab_size - размер словарей (одинаковый в силу зеркальности), 
    length_of_corpus - длинна корпуса
    """
    word_to_index= dict()
    index_to_word = dict()
    corpus = []
    count = 0
    vocab_size = 0
    
    for word in text.split():
        word = word.lower()
        corpus.append(word)
        if word_to_index.get(word) == None:
            word_to_index.update ( {word : count})
            index_to_word.update ( {count : word })
            count  += 1
    vocab_size = len(word_to_index)
    length_of_corpus = len(corpus)
    
    return word_to_index, index_to_word, corpus, vocab_size, length_of_corpus


def get_one_hot_vectors(target_word,
                        context_words,
                        vocab_size,
                        word_to_index):
    """
    генерация OHE векторов для отдельных слов
    
    вход:
    target_word - целевое слово,
    context_words - слова окружения,
    vocab_size - размер словаря,
    word_to_index - индекс слова
    
    выход:
    trgt_word_vector - вектор контекстного слова target_word,
    ctxt_word_vector - контекстный вектор слова (мекти слов 
    окоружения для данного target_word)
    
    """
    trgt_word_vector = np.zeros(vocab_size)
    
    index_of_word_dictionary = word_to_index.get(target_word) 
    
    trgt_word_vector[index_of_word_dictionary] = 1
    
    ctxt_word_vector = np.zeros(vocab_size)
    
    for word in context_words:
        index_of_word_dictionary = word_to_index.get(word) 
        ctxt_word_vector[index_of_word_dictionary] = 1 # считает только одно слово в контексте. 
						       # В случае поворения слова - будет ошибка (тольок одно слово будет учтено)
        
    return trgt_word_vector,ctxt_word_vector



def generate_training_data(corpus, 
                           window_size, 
                           vocab_size, 
                           word_to_index, 
                           length_of_corpus):
    """
    генерация тренировочных данных вида (target_words, context_words)
    вход:
    corpus - копрус слов для обучения, 
    window_size - размер окна для контестных слов, 
    vocab_size - размер словаря, 
    word_to_index - словарь word_to_index, 
    length_of_corpus - длинна корпуса слов, 
    sample (по умолчанию None) - список примеров
    
    выход:
    training_data - список данных для обучения,
    training_sample_words - список примеров
    
    """

    training_data =  []
    training_sample_words =  []
    for i,word in enumerate(corpus):

        index_target_word = i
        target_word = word
        context_words = []

        #when target word is the first word
        
        context_words =[word for word in
                        corpus[max(0, i-window_size):
                               min(length_of_corpus-1,i+window_size+1)]
                        if word != corpus[i]]
        

        trgt_word_vector,ctxt_word_vector = get_one_hot_vectors(target_word,
                                                                context_words,
                                                                vocab_size,
                                                                word_to_index)
        training_data.append([trgt_word_vector,ctxt_word_vector])   
        
        
    return training_data


def forward_prop(weight_inp_hidden,
                 weight_hidden_output,
                 target_word_vector):
    """
    прямой этап обучения.
    вход:
    weight_inp_hidden - матрица весов скрытого слоя,
    weight_hidden_output - матрица весов выходного слоя,
    target_word_vector - вектор слова
    
    выход:
    y_predicted - предсказанный вектор, 
    hidden_layer - скрытый слой, 
    u - мanрица U
    
    """
    hidden_layer = np.dot(weight_inp_hidden.T, target_word_vector)
    
    u = np.dot(weight_hidden_output.T, hidden_layer)
    
    y_predicted = softmax(u)
    
    return y_predicted, hidden_layer, u
  
def softmax(x):
    """Compute the softmax function for each row of the input x.
    It is crucial that this function is optimized for speed because
    it will be used frequently in later code. 

    Arguments:
    x -- A D dimensional vector or N x D dimensional numpy matrix.
    Return:
    x -- You are allowed to modify x in-place
    """
    orig_shape = x.shape

    if len(x.shape) > 1:
        # Matrix
        tmp = np.max(x, axis=1)
        x -= tmp.reshape((x.shape[0], 1))
        x = np.exp(x)
        tmp = np.sum(x, axis=1)
        x /= tmp.reshape((x.shape[0], 1))
    else:
        # Vector
        tmp = np.max(x)
        x -= tmp
        x = np.exp(x)
        tmp = np.sum(x)
        x /= tmp

    assert x.shape == orig_shape
    return x

def calculate_error(y_pred,context_words):
    """
    подсчёт ошибки
    
    вход
    y_pred,
    context_words 
    
    выход
    total_error
    """
    
    total_error = [None] * len(y_pred)
    index_of_1_in_context_words = {}
    
    for index in np.where(context_words == 1)[0]:
        index_of_1_in_context_words.update ( {index : 1} )
        
    number_of_1_in_context_vector = len(index_of_1_in_context_words)
    
    for i,value in enumerate(y_pred):
        
        if index_of_1_in_context_words.get(i) != None:
            total_error[i]= (value-1) + ( (number_of_1_in_context_vector -1) * value)
        else:
            total_error[i]= (number_of_1_in_context_vector * value)
            
            
    return  np.array(total_error)


def backward_prop(weight_inp_hidden,
                  weight_hidden_output,
                  total_error, 
                  hidden_layer, 
                  target_word_vector,
                  learning_rate):
    """
    обратное распространение ошибки
    
    вход
    weight_inp_hidden - веса входного слоя,
    weight_hidden_output - веса выходного слоя,
    total_error- общая ошибка, 
    hidden_layer - скрытый слой, 
    target_word_vector - целевое слово,
    learning_rate - величина сдвига по градиентному спуску
    
    выход
    weight_inp_hidden - веса входного слоя (модифицированные),
    weight_hidden_output - веса выходного слоя (модифицированные)
    """
    
    dl_weight_inp_hidden = np.outer(target_word_vector, np.dot(weight_hidden_output, total_error.T))
    dl_weight_hidden_output = np.outer(hidden_layer, total_error)
    

    weight_inp_hidden = weight_inp_hidden - (learning_rate * dl_weight_inp_hidden)
    weight_hidden_output = weight_hidden_output - (learning_rate * dl_weight_hidden_output)
    
    return weight_inp_hidden,weight_hidden_output


def calculate_loss(u,ctx):
    """
    подсчёт total loss
    
    вход
    u - вектор U,
    ctx - контекст,
    
    выход
    total_loss 
    """    
    sum_1 = 0
    for index in np.where(ctx==1)[0]:
        sum_1 = sum_1 + u[index]
    
    sum_1 = -sum_1
    sum_2 = len(np.where(ctx==1)[0]) * np.log(np.sum(np.exp(u)))
    
    total_loss = sum_1 + sum_2
    return total_loss

def train_ww(word_embedding_dimension,
             window_size,
             epochs,
             training_data,
             learning_rate,
             interval=-1):
    
    weights_input_hidden = np.random.uniform(-1, 1, (vocab_size, word_embedding_dimension))
    weights_hidden_output = np.random.uniform(-1, 1, (word_embedding_dimension, vocab_size))
    

    
    for epoch in range(epochs):
        loss = 0

        for target,context in training_data:
            y_pred, hidden_layer, u = forward_prop(weights_input_hidden,weights_hidden_output,target)

            total_error = calculate_error(y_pred, context)

            weights_input_hidden,weights_hidden_output = backward_prop(
                weights_input_hidden,weights_hidden_output ,total_error, hidden_layer, target,learning_rate
            )

            loss_temp = calculate_loss(u,context)
            loss += loss_temp
        


    return np.array(weights_input_hidden)




def train(data,
          window_size = 2,
          epochs = 100,
          dim = 50,
          learning_rate = 0.01,):
    word_to_index, index_to_word, corpus,vocab_size, length_of_corpus = generate_dictinoary_data(data)
    training_data = generate_training_data(corpus, 
                                           window_size,
                                           vocab_size,
                                           word_to_index,
                                           length_of_corpus)
    
    weights = train(dim,window_size,epochs,training_data,learning_rate)

    w2v_dict = dict(zip(list(index_to_word.values), weights))
    return w2v_dict





